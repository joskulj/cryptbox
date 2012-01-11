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

import os.path

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
        self._rootpath = rootpath
        self._relpath = None
        self._timestamp = None
        if filepath:
            self.set_filepath(filepath)

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

    def set_timestamp(self, timestamp):
        """
        sets the timestamp
        Parameters:
        - timestamp
          tirmestamp to set
        """
        self._timestamp = timestamp

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

    def get_timestamp(self):
        """
        Returns:
        - timestamp
        """
        return self._timestamp

