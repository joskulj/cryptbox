#!/usr/bin/env python

# cryptbox - main routine 
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

import sys

import cryptboxgtk

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

