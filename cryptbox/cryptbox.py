#!/usr/bin/env python

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

import socket
import sys
import time

import cryptboxgtk

from threading import Thread

# Application constants
CRYPTBOX_PORT = 5000
CRYPTBOX_RUNNER_INTERVAL = 10
CRYPTBOX_LISTENER_INTERVAL = 2

# State of the Runner Thread
RUNNER_STATE_NOT_STARTED = 0
RUNNER_STATE_RUNNING = 1
RUNNER_STATE_STOPPING = 2
RUNNER_STATE_PAUSING = 3

# Commands to control the Runner Thread
COMMAND_STOP = "stop"
COMMAND_PAUSE = "pause"
COMMAND_CONTINUE = "continue"

COMMAND_LIST = [ COMMAND_STOP, COMMAND_PAUSE, COMMAND_CONTINUE ]

class Runner(object):
    """
    class to run CryptBox synchronization
    """

    def __init__(self):
        """
        creates an instance
        """
        self._state = STATE_NOT_STARTED
        self._sleep_interval = CRYPTBOX_RUNNER_INTERVAL

    def is_running(self):
        """
        Returns:
        - True:  server is running
        - False: server is not running
        """
        return self._state != STATE_STOPPING

    def stop(self):
        """
        signals the thread to stop
        """
        self._state = STATE_STOPPING

    def start_pausing(self):
        """
        signals the thread to pause
        """
        self._state = STATE_PAUSING

    def stop_pausing(self):
        """
        signals the thread to stop pausing
        """
        self._state = STATE_RUNNING

    def start(self):
        """
        starts the thread
        """
        self._state = STATE_RUNNING
        while self.is_running():
            print "loop entered."
            if self._state == STATE_RUNNING:
                print "RunnerThread running."
                # TODO: start downloader
                # TODO: start uploader
            if self._state == STATE_PAUSING:
                print "RunnerThread paused."
            print "sleeping."
            time.sleep(self._sleep_interval)
            print "wake up."
        print "SyncThread stopped."

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
        print "DaemonListenerThread started."
        flag = True
        while flag:
            print "Read socket"
            data, address = self._socket.recvfrom(256)
            print "ListenerThread received: " + data
            if data == COMMAND_STOP:
                self._runner.stop()
                flag = False
            if data == COMMAND_PAUSE:
                self._runner.start_pausing()
            if data == COMMAND_CONTINUE:
                self._runner.stop_pausing()
            time.sleep(self._sleep_interval)
        print "DaemonListenerThread stopped."

class DaemonClient(object):
    """
    client to communicate with the listener thread
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


def print_usage():
    """
    prints the help text about using cryptbox
    """
    print "usage: cryptbox [OPTION]"
    print ""
    print "Use one of the following options:"
    print ""
    print "  --config   configure cryptbox"
    print "  --start    start the cryptbox daemon"
    print "  --stop     stop the cryptbox daemon"

def configure():
    """
    configure cryptbox
    """
    cryptboxgtk.show_config_window()

def start():
    """
    starts the cryptbox daemon
    """
    pass

def stop():
    """
    stops the cryptbox daemon
    """
    pass

if __name__ == "__main__":
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
        else:
            print_usage()

