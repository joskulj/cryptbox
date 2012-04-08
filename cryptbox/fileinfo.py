# cryptbox - class to manage file information
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
import getpass

from config import *
from couchhelper import *

FILEINFO_STATE_UPLOADED = "uploaded"
FILEINFO_STATE_DOWNLOADED = "downloaded" 
FILEINFO_STATE_DELETED = "deleted"

class FileInfoDatabase(object):
    """
    class to access file state information
    """

    def __init__(self):
        """
        creates an instance
        """
        user = getpass.getuser()
        database_name = "cryptbox-%s" % user
        self._database = CouchDatabase(database_name)
        config = CryptBoxConfig()
        self._rootpath = config.get_source_directory()

    def get_all(self):
        """
        gets all file state information
        Returns:
        - list of FileInfo instances
        """
        result = []
        for doc_id in self._database.get_document_list():
            doc = self._database.load_document(doc_id)
            relpath = doc.get_value("relpath")
            fileinfo = FileInfo(self._rootpath, relpath)
            print fileinfo.get_relative_path()
            result.append(fileinfo)
        return result

class FileInfo(object):
    """
    class to manage file information
    """

    def __init__(self, rootpath, filepath=None):
        """
        creates an instance
        Parameters:
        - rootpath
          path that represents the root
        - filepath
          file path to set
        """
        self._database = self.init_database()
        self._rootpath = rootpath
        self._relpath = None
        self._file_timestamp = None
        self._size = None
        self._state = None
        self._state_timestamp = None
        if filepath:
            self.set_filepath(filepath)
            self.read_state()

    def init_database(self):
        """
        inits the database to store state information
        Returns:
        - CouchDatabase instance
        """
        user = getpass.getuser()
        database_name = "cryptbox-%s" % user
        return CouchDatabase(database_name)

    def set_filepath(self, filepath):
        """
        sets the (absolute) file path
        Parameters:
        - filepath
          (absolute) file path to set
        """
        if filepath.startswith(self._rootpath):
            rootlen = len(self._rootpath)
            if not self._rootpath.endswith("/"):
                rootlen = rootlen + 1
            self._relpath = filepath[rootlen:]
        else:
            self._relpath = filepath

    def set_relative_path(self, relpath):
        """
        sets the relative file path to set
        Parameters:
        - relpath
          relative file path to set
        """
        self._relpath = relpath

    def update_state(self, state, state_timestamp):
        """
        sets the state and the corresponding timestamp
        Parameters:
        - state
          state to set
        - state_timestamp
          tirmestamp of last state change
        """
        self._state = state
        self._state_timestamp = state_timestamp
        self.save_state()

    def scan(self):
        """
        scans the file properties from the file system
        """
        path = self.get_absolute_path()
        if os.path.exists(path):
            self._file_timestamp = os.path.getmtime(path)
            self._size = os.path.getsize(path)
        else:
            self._timestamp = None
            self._size = None

    def read_state(self):
        """
        reads the state information
        """
        key = CouchKey([self._relpath])
        doc = self._database.load_document(key.get_key())
        if doc:
            self._state = doc.get_value("state")
            self._state_timestamp = doc.get_value("state_timestamp")

    def save_state(self):
        """
        saves the state information
        """
        key = CouchKey([self._relpath])
        doc = self._database.load_document(key.get_key())
        if doc == None:
            doc = CouchDocument(key.get_key())
        doc.set_value("relpath", self._relpath)
        doc.set_value("state", self._state)
        doc.set_value("state_timestamp", self._state_timestamp)
        self._database.save_document(doc)

    def exists(self):
        """
        checks, if the file exists
        Returns:
        - True: file exists
        - False: file does not exist
        """
        self.scan()
        return (self._size != None)

    def get_relative_path(self):
        """
        Returns:
        - relative path
        """
        return self._relpath

    def get_absolute_path(self, rootpath=None):
        """
        returns the absolute path
        Parameters:
        - rootpath
          alternative root path to use (optional)
        Returns:
        - absolute path
        """
        result = None
        if rootpath:
            result = os.path.join(rootpath, self._relpath)
        else:
            result = os.path.join(self._rootpath, self._relpath)
        return result

    def get_file_timestamp(self):
        """
        Returns:
        - timestamp of the file
        """
        return self._file_timestamp

    def get_state(self):
        """
        Returns:
        - state of the file
        Returns:
        - state of the file
        """
        return self._state

    def get_state_timestamp(self):
        """
        Returns:
        - timestamp of the state
        """
        return self._state_timestamp

    def get_size(self):
        """
        Returns:
        - fils size
        """
        return self._size

    def delete_file(self, timestamp):
        """
        deletes the corresponding file
        Parameters:
        - timestamp
          timestamp for deleting file
        Returns:
        - True:  file was deleted
        - False: deleting the file failed
        """
        flag = True
        try:
            path = self.get_absolute_path()
            os.remove(path)
        except OSError:
            flag = False
        if flag:
            self.update_state(FILEINFO_STATE_DELETED, timestamp)
        return flag

class FileInfoList(object):
    """
    class to manage a list of FileInfo instances
    """

    def __init__(self):
        """
        creates an instance
        """
        self._dict = {}
        self._list = []

    def append(self, fileinfo):
        """
        appends a FileInfo instance
        Parameters:
        - fileinfo
          FileInfo instance to append
        """
        key = fileinfo.get_relative_path()
        self._dict[key] = fileinfo
        self._list.append(fileinfo)

    def get_entries(self):
        """
        Returns:
        - list of entries
        """
        return self._list

    def get_entry(self, relpath):
        """
        returns FileInfo by a relative path
        Parameters:
        Return:
        - FileInfo
        """
        result = None
        if relpath in self._dict().keys():
            result = self._dict[relpath]
        return result

