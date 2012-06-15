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

import os.path

class CryptBoxConfig(object):
    """
    class to manage the cryptbox configuration
    """

    def __init__(self):
        """
        creates an instance
        """
        self._source_directory = None
        self._destination_directory = None
        self._password_salt = None
        self._password_repeat_hash = 0
        if self.exists():
            self.load()

    def get_config_filepath(self):
        """
        Returns:
        - filepath of the config file
        """
        return os.path.expanduser("~/.cryptboxrc")

    def exists(self):
        """
        checks if the config file exists
        Returns:
        - True:  config file exists
        - False: config file doesn't exist
        """
        return os.path.exists(self.get_config_filepath())

    def set_source_directory(self, directory):
        """
        sets the source directory
        Parameters:
        - directory
          source directory to set
        """
        self._source_directory = directory

    def set_destination_directory(self, directory):
        """
        sets the destination directory
        Parameters:
        - directory
           directory to set
        """
        self._destination_directory = directory

    def set_password_salt(self, salt):
        """
        sets salt value for password hash
        Parameters:
        - salt
          salt value for password hash
        """
        self._password_salt = salt

    def set_password_repeat_hash(self, repeat_hash):
        """
        sets the value for repeating pashword hashing
        Parameters:
        - repeat_hash
          value for repeating password hashing
        """
        self._password_repeat_hash = repeat_hash

    def get_source_directory(self):
        """
        Returns:
        - the source directory
        """
        return self._source_directory

    def get_destination_directory(self):
        """
        Returns:
        - the destination directory
        """
        return self._destination_directory

    def get_password_salt(self):
        """
        Returns:
        - salt value for password hash
        """
        return self._password_salt

    def get_password_repeat_hash(self):
        """
        Returns:
        - value for repeating password hashing
        """
        return self._password_repeat_hash
 
    def load(self):
        """
        loads the config file
        Returns:
        - True:  config file was loaded
        - False: loading the config file failed
        """
        result = True
        filepath = self.get_config_filepath()
        try:
            config_file = open(filepath, "r")
            for line in config_file.readlines():
                if "=" in line:
                    pos = line.find("=")
                    key = line[0:pos].lstrip().rstrip()
                    value = line[pos + 1:].lstrip().rstrip()
                    if key == "source":
                        self._source_directory = value
                    elif key == "destination":
                        self._destination_directory = value
                    elif key == "password_salt":
                        self._password_salt = value
                    elif key == "password_repeat_hash":
                        try:
                            self._password_repeat_hash = int(value)
                        except ValueError:
                            self._password_repeat_hash = 0
                            print "Invalid Repeat Hash value %s." % value
                    else:
                        print "Invalid configuration key %s was ignored." % key
            config_file.close()
        except:
            result = False
        return result

    def save(self):
        """
        saves the config file
        Returns:
        - True:  config file was saved
        - False: saving the config file failed
        """
        result = True
        filepath = self.get_config_filepath()
        try:
            config_file = open(filepath, "w")
            config_file.write("# CryptBox configuration file\n")
            if self._source_directory:
                config_file.write("source = %s\n" % self._source_directory)
            if self._destination_directory:
                config_file.write("destination = %s\n" % self._destination_directory)
            if self._password_salt:
                config_file.write("password_salt = %s\n" % self._password_salt)
            config_file.write("password_repeat_hash = %s\n" % str(self._password_repeat_hash))
            config_file.close()
        except IOError:
            result = False
        return result
