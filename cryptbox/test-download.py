#!/usr/bin/env python

# cryptbox - tests the download of files
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

import time

from dirscanner import *
from cryptstore import *

if __name__ == "__main__":
    srcpath = "/home/joskulj/Cryptbox"
    destpath = "/home/joskulj/Dropbox"
    cryptstore = CryptStore()
    if cryptstore.has_password():
        print "existing password."
        cryptstore.set_password("test123")
        print normalize_key("test123")
    else:
        cryptstore.set_new_password("test123")
    for entry in cryptstore.get_entries():
        print entry.get_filepath()
        print entry.get_entry_id()
        print entry.get_timestamp()
        cryptstore.download_file(entry, srcpath)
