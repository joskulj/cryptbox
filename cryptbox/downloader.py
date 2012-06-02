# cryptbox - class to process downloads from the CryptStore
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

from config import *
from cryptlog import *
from fileinfo import *

class Downloader(object):
    """
    class to process downloads from the CryptStore
    """

    def __init__(self, cryptstore):
        """
        creates an instance
        Parameters:
        - cryptstore
          CryptStore instance to use
        """
        self._cryptstore = cryptstore
        config = CryptBoxConfig()
        self._rootpath = config.get_source_directory()

    def run(self):
        """
        executes the Downloader
        """
        for entry in self._cryptstore.get_entries():
            relpath = entry.get_filepath()
            entry_timestamp = entry.get_timestamp()
            fileinfo = FileInfo(self._rootpath, relpath)
            if entry.get_state() != FILEINFO_STATE_DELETED:
                download_flag = True
                if fileinfo.exists():
                    file_timestamp = fileinfo.get_file_timestamp()
                    if entry_timestamp - file_timestamp <= 1:
                        download_flag = False
                if download_flag:
                    self._cryptstore.download_file(entry, self._rootpath)
                    cryptlog("%s downloaded." % relpath)
            else:
                fileinfo.delete_file(time.time())

