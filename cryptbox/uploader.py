# cryptbox - class to process uploads to the CryptStore
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

from config import *
from cryptlog import *
from dirscanner import *
from debug import *
from fileinfo import *

class Uploader(object):
    """
    class to process uploads to the CryptStore
    """

    def __init__(self, cryptstore):
        """
        creates an instance
        Parameters:
        - cryptstore
          CryptStore instance to use
        """
        self._cryptstore = cryptstore

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
        debuglog = DebugLogger("cryptbox", "Uploader")
        debuglog.debug_value("fileinfo.relative_path", fileinfo.get_relative_path())
        debuglog.debug_value("fileinfo.exist", fileinfo.exists())
        debuglog.debug_value("fileinfo.file_timestamp", fileinfo.get_file_timestamp())
        debuglog.debug_value("fileinfo.state_timestamp", fileinfo.get_state_timestamp())
        if entry:
            debuglog.debug_value("entry.state", entry.get_state())
            debuglog.debug_value("entry.timestamp", entry.get_timestamp())
        else:
            debuglog.debug_value("entry", None)
        debuglog.debug(action)

 
    def run(self):
        """
        executes the Uploader
        """
        self.check_for_delete()
        self.check_for_upload()

    def check_for_delete(self):
        """
        check if files should be deleted
        """
        debuglog = DebugLogger("cryptbox", "Uploader.check_for_delete")
        database = FileInfoDatabase()
        for fileinfo in database.get_all():
            fileinfo.scan()
            if not fileinfo.exists():
                if fileinfo.get_state() != FILEINFO_STATE_DELETED:
                    delete_flag = True
                    filepath = fileinfo.get_relative_path()
                    file_timestamp = fileinfo.get_state_timestamp()
                    entry = self._cryptstore.get_entry(filepath)
                    entry_timestamp = entry.get_timestamp()
                    if entry.get_state() != FILEINFO_STATE_DELETED:
                        if entry_timestamp > file_timestamp:
                            self._debug("file not deleted", entry, fileinfo)
                            delete_flag = False
                    if delete_flag and entry.get_state() != FILEINFO_STATE_DELETED:
                        self._debug("file deleted", entry, fileinfo)
                        self._cryptstore.delete_file(entry)
                        cryptlog("%s deleted." % filepath)

    def check_for_upload(self):
        """
        check if files should be uploaded
        """
        config = CryptBoxConfig()
        srcpath = config.get_source_directory()
        scanner = DirScanner(srcpath)
        for fileinfo in scanner.get_list().get_entries():
            upload_flag = False
            fileinfo.scan()
            relpath = fileinfo.get_relative_path()
            storeentry = self._cryptstore.get_entry(relpath)
            if storeentry:
                file_timestamp = fileinfo.get_file_timestamp()
                store_timestamp = storeentry.get_timestamp()
                if file_timestamp > store_timestamp:
                    upload_flag = True
            else:
                upload_flag = True
            if upload_flag:
                self._debug("file uploaded", storeentry, fileinfo)
                self._cryptstore.upload_file(fileinfo)
                cryptlog("%s uploadad." % relpath)
            else:
                self._debug("no action", storeentry, fileinfo)
