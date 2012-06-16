#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# cryptbox - main application 
#
# Copyright 2012 Jochen Skulj, jochen@jochenskulj.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import os.path
import signal
import socket
import sys
import time

import cryptboxgtk

from subprocess import Popen, PIPE
from threading import Thread

from cryptboxgtk import *
from cryptlog import *
from cryptstore import *
from config import *
from dirscanner import *
from downloader import *
from fileinfo import *
from uploader import *

# Application constants
CRYPTBOX_PORT = 5000
# interval for checking: 15 minutes
CRYPTBOX_RUNNER_INTERVAL = 900
CRYPTBOX_LISTENER_INTERVAL = 2

# State of the Runner Thread
RUNNER_STATE_NOT_STARTED = 0
RUNNER_STATE_RUNNING = 1
RUNNER_STATE_STOPPING = 2

# Commands to control the Runner Thread
COMMAND_STOP = "stop"

# Numbers of log entries to store before saving
MAX_LOG_COUNTER = 50

class PIDLock(object):
    """
    utility class to check if CryptBox is already running
    """

    def __init__(self):
        """
        creates an instance
        """
        self._filepath = os.path.expanduser("~/.cryptbox.pid")

    def write(self):
        """
        writes a lock file
        """
        pid = os.getpid()
        try:
            pidfile = open(self._filepath, "w")
            pidfile.write(str(pid))
            pidfile.close()
        except IOError:
            print "Unable to write: %s" % self._filepath

    def exists(self):
        """
        checks if the lock files exists
        Returns:
        - True:  lock file exists
        - False: lock file does not exists
        """
        return os.path.exists(self._filepath)

    def read(self):
        """
        reads the lock file
        Returns:
        - PID in the lock file or None
        """
        result = None
        if self.exists():
            try:
                pidfile = open(self._filepath, "r")
                line = pidfile.readline()
                pidfile.close()
                result = int(line)
            except IOError:
                print "Unable to read: %s" % self._filepath
        return result

    def delete(self):
        """
        deletes the lock file
        """
        try:
            os.remove(self._filepath)
        except OSError:
            print "Unable to delete %s" % self._filepath

    def is_process_running(self, pid):
        """
        checks if a process with a given pid is running
        Parameters:
        - pid
          pid to check
        Returns:
        - True:  process is running
        - False: process doesn't exists
        """
        result = False
        process = Popen(['ps', '-eo' ,'pid,args'], stdout=PIPE, stderr=PIPE)
        stdout, notused = process.communicate()
        for line in stdout.splitlines():
            pid_string = line.split(' ')[1]
            try:
                running_pid = int(pid_string)
                if running_pid == pid:
                    result = True
                    break
            except ValueError:
                pass
        return result

    def check(self):
        """
        checks if CryptBox is running
        Returns:
        - True:  CryptBox is running
        - False: CryptBox is not running
        """
        result = False
        if self.exists():
            pid = self.read()
            if pid:
                if self.is_process_running(pid):
                    result = True
                else:
                    self.delete()
        return result

class Runner(object):
    """
    class to run CryptBox synch
    ronization
   """

    def __init__(self, cryptstore):
        """
        creates an instance
        Parameters:
        - cryptstore
          CryptStore instance to use
        """
        self._state = RUNNER_STATE_NOT_STARTED
        self._sleep_interval = CRYPTBOX_RUNNER_INTERVAL
        self._cryptstore = cryptstore
        self._uploader = Uploader(self._cryptstore)
        self._downloader = Downloader(self._cryptstore)
        self._sleep_counter = 0
        runner_instance = self

    def is_running(self):
        """
        Returns:
        - True:  server is running
        - False: server is not running
        """
        return self._state != RUNNER_STATE_STOPPING

    def stop(self):
        """
        signals the thread to stop
        """
        self._state = RUNNER_STATE_STOPPING
        self._sleep_counter = 0

    def start(self):
        """
        starts the thread
        """
        cryptlog("Syncronization started.")
        lock = PIDLock()
        lock.write()
        self._state = RUNNER_STATE_RUNNING
        log_counter = MAX_LOG_COUNTER
        while self.is_running():
            if self._state == RUNNER_STATE_RUNNING:
                cryptlog("Checking password timestamp ...")
                if not self._cryptstore.check_password_timestamp():
                    cryptlog("Password seemed to be changed.")
                    client = RunnerClient(CRYPTBOX_PORT)
                    client.stop()
                else:
                    cryptlog("Refreshing CryptStore ...")
                    self._cryptstore.refresh()
                    cryptlog("Running Uploader ...")
                    self._uploader.run()
                    cryptlog("Running Downloader ...")
                    self._downloader.run()
                log_counter = log_counter - 1
                if log_counter == 0:
                    save_cryptlog()
                    log_counter = MAX_LOG_COUNTER
            self._sleep_counter = self._sleep_interval
            while self._sleep_counter > 0:
                time.sleep(1)
                self._sleep_counter = self._sleep_counter - 1
        cryptlog("Syncronization stopped.")
        lock.delete()
        save_cryptlog()

class ListenerThread(Thread):
    """
    Thread to recieve commands and controls the Runner object
    """

    def __init__(self, runner, port):
        """
        create instance
        Parameters:
        - sync_thread
          runner object to control
        - port
          port to communicate with the client
        """
        Thread.__init__(self)
        self._runner = runner
        self._socket = self.init_socket(port)
        self._sleep_interval = CRYPTBOX_LISTENER_INTERVAL

    def init_socket(self, port):
        """
        initializes the socket to communicate with the client
        Parameters:
        - port
          port to use
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(("", port))
        return server_socket

    def run(self):
        """
        starts the thread
        """
        flag = True
        while flag:
            data, address = self._socket.recvfrom(256)
            if data == COMMAND_STOP:
                self._runner.stop()
                flag = False
            time.sleep(self._sleep_interval)

class RunnerClient(object):
    """
    client to communicate with the Listener Thread
    """

    def __init__(self, port):
        """
        create instance
        Parameters:
        - port
          port to use
        """
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.connect(("localhost", self._port))

    def send(self, data):
        """
        sends data to the server
        Parameters:
        - data
          data to send
        """
        self._socket.sendto(data, ("localhost", self._port))

    def stop(self):
        """
        signals the server to stop
        """
        self.send(COMMAND_STOP)

def on_sigterm(sig, frame):
    """
    handles SIGTERM sinal
    Parameters:
    - sig
      recieved signal
    - frame
      stack frame
    """
    cryptlog("SIGTERM/SIGINT recieved")
    client = RunnerClient(CRYPTBOX_PORT)
    client.stop()

def print_usage():
    """
    prints the help text about using cryptbox
    """
    print "usage: %s [OPTION]" % sys.argv[0]
    print ""
    print "Use one of the following options:"
    print ""
    print "  --config        configure cryptbox"
    print "  --start         start the cryptbox daemon"
    print "  --stop          stop the cryptbox daemon"
    print "  --new-password  changes the password"
    print "  --download      download files from the destination directory"
    print "  --upload        upload files to the destination directory"
    print "  --purge         purge deleted files from destination directory"
    print "  --src-list      list information of the source directory"
    print "  --dest-list     list information of the destination directory"

def init_cryptstore():
    """
    creates an cryptstore instance
    Returns:
    - cryptstore instance or None if login failed
    """
    result = CryptStore()
    if result.has_password():
        flag = show_login_window(result)
        if not flag:
            result = None
    else:
        password = show_new_password_window()
        if password:
            result.set_new_password(password)
        else:
            result = None
    return result

def timestamp_string(timestamp_float):
    """
    converts a float timestamp into a string
    Parameters:
    - timestamp_float
      float representation of a timestamp
    Returns:
    - string representation of the timestamp
    """
    result = "(none)"
    if timestamp_float:
        timestamp_struct = time.localtime(timestamp_float)
        result = time.strftime("%c", timestamp_struct)
    return result

def check_lock():
    """
    checks if CryptBox process is running. If such a process is
    running, the program will be stopped.
    """
    lock = PIDLock()
    if lock.check():
        print "CryptBox already running."
        print "Unable to execute command."
        sys.exit(0)

def configure():
    """
    configure cryptbox
    """
    check_lock()
    cryptboxgtk.show_config_window()

def start():
    """
    starts the cryptbox daemon
    """
    cryptstore = init_cryptstore()
    if cryptstore:
        signal.signal(signal.SIGTERM, on_sigterm)
        signal.signal(signal.SIGINT, on_sigterm)
        runner = Runner(cryptstore)
        listener = ListenerThread(runner, CRYPTBOX_PORT)
        listener.start()
        runner.start()
    else:
        print "starting cryptbox aborted."

def stop():
    """
    stops the cryptbox daemon
    """
    client = RunnerClient(CRYPTBOX_PORT)
    client.stop()

def new_password():
    """
    sets up a new password
    """
    check_lock()
    cryptstore = init_cryptstore()
    set_cryptlog_verbose(True)
    cryptlog("Changing password ...")
    # Update the local files
    if cryptstore:
        uploader = Uploader(cryptstore)
        uploader.run()
        downloader = Downloader(cryptstore)
        downloader.run()
    password = show_new_password_window()
    if password:
        # Change the password
        cryptstore = CryptStore()
        cryptstore.set_new_password(password, False)
        # Upload all local files with new password
        config = CryptBoxConfig()
        srcpath = config.get_source_directory()
        scanner = DirScanner(srcpath)
        timestamp = time.time()
        for fileinfo in scanner.get_list().get_entries():
            fileinfo.scan()
            if fileinfo.exists():
                fileinfo.set_timestamp(timestamp)    
                relpath = fileinfo.get_relative_path()
                cryptstore.upload_file(fileinfo)
                cryptlog("%s uploaded." % relpath)
        cryptlog("Changing password completed.")
    else:
        cryptlog("Changing password canceled.")
    save_cryptlog()

def download():
    """
    downloads files from the destination directory
    """
    check_lock()
    cryptstore = init_cryptstore()
    set_cryptlog_verbose(True)
    cryptlog("Download started.")
    downloader = Downloader(cryptstore)
    downloader.run()
    cryptlog("Download finished.")
    save_cryptlog()

def upload():
    """
    uploads files to the destination directory
    """
    check_lock()
    cryptstore = init_cryptstore()
    set_cryptlog_verbose(True)
    cryptlog("Upload started.")
    uploader = Uploader(cryptstore)
    uploader.run()
    cryptlog("Upload finished.")
    save_cryptlog()

def destination_list():
    """
    lists the meta information of the destination directory
    """
    cryptstore = init_cryptstore()
    if cryptstore:
        for entry in cryptstore.get_entries():
            print "id: %s" % entry.get_entry_id()
            print "filepath: %s" % entry.get_filepath()
            print "state: %s" % entry.get_state()
            timestamp = timestamp_string(entry.get_timestamp()) 
            print "timestamp: %s" % timestamp
            print ""
    else:
        print "Accessing cryptstore failed."

def source_list():
    """
    lists the meta information of the source directory
    """
    config = CryptBoxConfig()
    srcpath = config.get_source_directory()
    scanner = DirScanner(srcpath)
    fileinfolist = scanner.get_list()
    for entry in fileinfolist.get_entries():
        print "filepath: %s" % entry.get_relative_path()
        timestamp = timestamp_string(entry.get_file_timestamp())
        print "file timestamp: %s" % timestamp
        print "state: %s" % entry.get_state()
        timestamp = timestamp_string(entry.get_state_timestamp())
        print "state timestamp: %s" % timestamp
        print ""

def purge():
    """
    purge files that were deleted
    """
    check_lock()
    cryptstore = init_cryptstore()
    set_cryptlog_verbose(True)
    pathlist = cryptstore.purge()
    if len(pathlist) == 0:
        cryptlog("no files purged.")
    else:
        for path in pathlist:
            cryptlog("%s purged." % path)

def main():
    """
    main function
    """
    if len(sys.argv) < 2:
        print_usage()
    else:
        option = sys.argv[1]
        if option == "--config":
            configure()
        elif option == "--start":
            start()
        elif option == "--stop":
            stop()
        elif option == "--new-password":
            new_password()
        elif option == "--download":
            download()
        elif option == "--upload":
            upload()
        elif option == "--dest-list":
            destination_list()
        elif option == "--src-list":
            source_list()
        elif option == "--purge":
            purge()
        else:
            print_usage()

if __name__ == "__main__":
    main()
