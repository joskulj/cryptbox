# cryptbox - class to manage the cryptbox configuration
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

KEY_SOURCE_DIRECTORY = "source-directory"
KEY_DESTINATION_DIRECTORY = "destination-directory"
KEY_PASSWORD_HASH = "password-hash"

class CryptBoxConfig(object):
    """
    class to manage the cryptbox configuration
    """

    def __init__(self):
        """
        creates an instance
        """
        self._dict = { }
        self._dict[KEY_SOURCE_DIRECTORY] = ""
        self._dict[KEY_DESTINATION_DIRECTORY] = ""
        self._dict[KEY_PASSWORD_HASH] = ""

    def set_source_directory(self, directory):
        """
        sets the source directory
        Parameters:
        - directory
          source directory to set
        """
        self._dict[KEY_SOURCE_DIRECTORY] = directory

    def set_destination_directory(self, directory):
        """
        sets the destination directory
        Parameters:
        - directory
           directory to set
        """
        self._dict[KEY_DESTINATION_DIRECTORY] = directory

