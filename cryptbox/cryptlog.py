# cryptbox - logging for cryptbox 
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

import os.path
import time

CRYPTLOG_MAX_LENGTH = 500

cryptlog_array = None

def cryptlog(message):
    """
    logs a message
    Parameters:
    - message
      message to log
    """
    global cryptlog_array
    if cryptlog_array == None:
        load_cryptlog()
    timestamp = time.asctime(time.localtime())
    line = "%s: %s" % (timestamp, message)
    cryptlog_array.append(line)
    if len(cryptlog_array) > CRYPTLOG_MAX_LENGTH:
        del cryptlog_array[0]

def get_cryptlog_path():
    """
    returns the path of the log file
    Return:
    - path of the log file
    """
    return os.path.expanduser("~/.cryptbox.log")

def load_cryptlog():
    """
    loads the existing log file
    """
    global cryptlog_array
    path = get_cryptlog_path()
    if os.path.exists(path):
        try:
            logfile = open(path, "r")
            lines = []
            for line in logfile.readlines():
                lines.append(line.strip())
            logfile.close()
            cryptlog_array = lines
        except IOError:
            print "Unable to read: %s" % path
    else:
        cryptlog_array = []

def save_cryptlog():
    """
    saves the logfile
    """
    global cryptlog_array
    path = get_cryptlog_path()
    try:
        logfile = open(path, "w")
        newarray = []
        for line in cryptlog_array:
            if line:
                logfile.write(line)
                logfile.write("\n")
                newarray.append(line)
        logfile.close()
        cryptlog_array = newarray
    except IOError:
        print "Unable to write: %s" % path
