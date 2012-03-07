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
from dirscanner import *
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
        database = FileInfoDatabase()
        for fileinfo in database.get_all():
            if not fileinfo.exists():
                if fileinfo.get_state() != FILE_INFO_STATE_DELETED:
                    filepath = fileinfo.get_relative_path()
                    entry = self._cryptstore.get_entry(filepath)
                    # TODO: compare time stamps
                    self._cryptstore.delete_file(entry)

    def check_for_upload(self):
        """
        check if files should be uploaded
        """
        print "check_for_upload()"
        config = CryptBoxConfig()
        srcpath = config.get_source_directory()
        scanner = DirScanner(srcpath)
        for fileinfo in scanner.get_list().get_entries():
            upload_flag = True
            relpath = fileinfo.get_relative_path()
            storeentry = self._cryptstore.get_entry(relpath)
            if storeentry:
                print "src timestamp: " + fileinfo.get_timestamp()
                print "dest timestamp: " + storeentry.get_timestamp()
            print relpath
        pass
