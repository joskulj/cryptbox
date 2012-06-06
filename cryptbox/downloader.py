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
from debug import *
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

    def _debug(self, action, entry, fileinfo):
        """
        logs debug information
        Parameters:
        - action
          action to log
        - entry
          corresponding cryptstore entry
        - fileinfo
          corresponding file info
        """
        debuglog = DebugLogger("cryptbox", "Downloader")
        debuglog.debug_value("entry.filepath", entry.get_filepath())
        debuglog.debug_value("entry.state", entry.get_state())
        debuglog.debug_value("entry.timestamp", entry.get_timestamp())
        debuglog.debug_value("fileinfo.exist", fileinfo.exists())
        debuglog.debug_value("fileinfo.file_timestamp", fileinfo.get_file_timestamp())
        debuglog.debug(action)

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
                        # the file in the source directory is newer than
                        # in the destination directory; it will not be
                        # downloaded.
                        download_flag = False
                        self._debug("file not downloaded", entry, fileinfo)
                if download_flag:
                    self._debug("file downloaded", entry, fileinfo)
                    self._cryptstore.download_file(entry, self._rootpath)
                    cryptlog("%s downloaded." % relpath)
            else:
                delete_flag = True
                if fileinfo.exists():
                    file_timestamp = fileinfo.get_file_timestamp()
                    if entry_timestamp - file_timestamp <= 1:
                        # the file in the source directory was modified
                        # after the file was deleted in  the destination
                        # directory; it will be not deleted but uploaded
                        # again.
                        delete_flag = False
                        self._debug("file uploaded", entry, fileinfo)
                        self._crypstore.upload_file(fileinfo)
                        cryptlog("%s uploaded." % relpath)
                    if delete_flag:
                        self._debug("file deleted", entry, fileinfo)
                        fileinfo.delete_file(time.time())
                        cryptlog("%s deleted." % relpath)

