# cryptbox - class to scan the source directory
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

import glob
import os
import os.path

from fileinfo import *

class DirScanner(object):
    """
    class to scan the source directory
    """

    def __init__(self, rootpath):
        """
        creates an instance
        Parameters:
        - rootpath
          path of the root to scen
        """
        self._list = FileInfoList()
        self._rootpath = rootpath
        self._scan(self._rootpath)

    def _scan(self, path):
        """
        scans the files of a given directory and its subdirectories
        and creates a FileInfo instance for each file
        Parameters:
        - path
          path of the directory to scan
        """
        dirlist = []
        for entry in glob.glob(os.path.join(path, "*")):
            if os.path.isfile(entry):
                fileinfo = FileInfo(self._rootpath, entry)
                fileinfo.scan()
                self._list.append(fileinfo)
            if os.path.isdir(entry):
                dirlist.append(entry)
        for entry in dirlist:
            self._scan(entry)

    def get_list(self):
        """
        Returns:
        - FileInfoList
        """
        return self._list

