# debug - debugging functions
#
# Copyright 2010 Jochen Skulj, jochen@jochenskulj.de
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
import sys
import time

from cStringIO import StringIO

DEBUG_LEVEL_INFO = "INFO"
DEBUG_LEVEL_ERROR = "ERROR"

debug_flag = None
error_flag = None

def get_log_filename():
    """
    Returns:
    - full path of the log file
    """
    return os.path.join(os.getcwd(), "_debug.log")

def delete_log_file():
    """
    deletes previous log file
    """
    fname = get_log_filename()
    try:
        os.remove(fname)
    except:
        message = "Unable to delete: " + fname
        sys.stderr.write(message + "\n")

def open_log_file():
    """
    opens log file
    Returns:
    - opened log file or None
    """
    global error_flag
    fd = None
    try:
        fname = get_log_filename()
        fd = open(fname, "a")
    except:
        if error_flag == None:
            message = "Unable to open: " + get_log_filename()
            sys.stderr.write(message + "\n")
        error_flag = True
    return fd

def log_line(line, level=DEBUG_LEVEL_INFO):
    """
    logs a line
    Parameters:
    - line
      line to log
    - level
      debug level to use
    """
    logline = "[%s] %s\n" % (level, line)
    success = True
    fd = open_log_file()
    if fd != None:
        try:
            fd.write(logline)
            fd.close()
            success = True
        except:
            success = False
    else:
        success = False
    if success == False:
        sys.stderr.write(line)

def get_debug_flag():
    """
    determines if debugging is switched on
    Returns:
    - True:  debugging switched on
    - False: debugging switched off
    """
    global debug_flag
    if debug_flag == None:
        debug_flag = False
        for arg in sys.argv:
            if arg == "--debug":
                delete_log_file()
                debug_flag = True
    return debug_flag

def debug(line):
    """
    debugs a line
    Parameters:
    - line
      line to debug
    """
    if get_debug_flag():
        log_line(line)

def debug_error(line):
    """
    debugs a line at error level
    Parameters:
    - line
      line to debug
    """
    if get_debug_flag():
        log_line(line, DEBUG_LEVEL_ERROR)

def debug_exception():
    """
    debugs the current exception
    """
    if get_debug_flag():
        line = sys.exc_type, ":", sys.exc_value
        log_line(line, DEBUG_LEVEL_ERROR)

def debug_value(label, value):
    """
    debugs a value
    - label
      label for a value
    - value
      value to log
    """
    if get_debug_flag():
        stringio = StringIO()
        stringio.write(label)
        if value:
            stringio.write(" = ")
            stringio.write(str(value))
        else:
            stringio.write(" = (None)")
        log_line(stringio.getvalue())

class DebugLogger(object):
    """
    class for logging debug information
    """

    def __init__(self, application, scope):
        """
        creates an instance
        Parameters:
        - application
          name of the current application
        - scope
          scope of debugging
        """
        self._application = application
        self._scope = scope
        self._debug_flag = self.get_debug_flag()
        self._debug_filename = self.get_debug_filename()
        self._error_flag = False

    def _open_log_file(self):
        """
        opens log file
        Returns:
        - opened log file or None
        """
        fd = None
        try:
            fd = open(self._debug_filename, "a")
        except IOError:
            if not self._error_flag:
                self._error_flag = True
                message = "Unable to open: %s\n" % self._debug_filename 
                sys.stderr.write(message)
            fd  = None
        return fd

    def _log_line(self, line, level=DEBUG_LEVEL_INFO):
        """
        logs a line
        Parameters:
        - line
          line to log
        - level
          debug level to use
        """
        if self._debug_flag:
            success = True
            tstamp = time.asctime(time.localtime())
            logline = "%s [%s] - %s: %s\n" % (tstamp, self._scope, level, line)
            fd = self._open_log_file()
            if fd != None:
                try:
                    fd.write(logline)
                    fd.close()
                    success = True
                except:
                    success = False
            if success == False:
                sys.stderr.write(line)

    def get_debug_flag(self):
        """
        determines if debugging is switched on
        Returns:
        - True:  debugging switched on
        - False: debugging switched off
        """
        result = False
        for arg in sys.argv:
            if arg == "--debug":
                result = True
        return result

    def get_debug_filename(self):
        """
        Returns:
        - filename of the debug file
        """
        path = os.path.expanduser("~")
        return "".join([path, "/.", self._application, ".debug"])

    def debug(self, line):
        """
        debugs a line
        Parameters:
        - line
          line to debug
        """
        self._log_line(line, DEBUG_LEVEL_INFO)

    def debug_error(self, line):
        """
        debugs a line at error level
        Parameters:
        - line
          line to debug
        """
        self._log_line(line, DEBUG_LEVEL_ERROR)

    def debug_exception(self):
        """
        debugs the current exception
        """
        if self._debug_flag:
            line = sys.exc_type, ":", sys.exc_value
            self._log_line(line, DEBUG_LEVEL_ERROR)

    def debug_value(self, label, value):
        """
        debugs a value
        - label
          label for a value
        - value
          value to log
        """
        if self._debug_flag:
            stringio = StringIO()
            stringio.write(label)
            if value:
                stringio.write(" = ")
                stringio.write(str(value))
            else:
                stringio.write(" = (None)")
            self._log_line(stringio.getvalue())


