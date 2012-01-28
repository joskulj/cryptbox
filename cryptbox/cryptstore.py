# cryptbox - class to store encrypted files
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

import getpass
import hashlib
import json
import os
import os.path
import random
import struct
import tempfile

from Crypto.Cipher import AES
from tempfile import *

from config import *
from cryptboxgtk import *

# helper functions for encryption and decryption

def normalize_key(key):
    """
    normalize a key to a valid length
    - key
      key to normalize
    Returns:
    - normalized keys
    """
    result = key
    targetlength = 16
    if len(key) > 16:
        targetlength = 24
    if len(key) > 24:
        targetlength = 32
    part = key
    while len(result) < targetlength:
        part = part[::-1]
        result = result + part
    return result[:targetlength]

def split_line(line, length):
    """
    splits a line into several substrings with a given
    length
    Parameters:
    - line
      line to split into substrings
    - length
      length of each substring
    Returns:
    - list of substrings
    """
    result = []
    pos = 0
    while pos + length < len(line):
        part = line[pos:pos + length]
        result.append(part)
        pos = pos + length
    if pos < len(line):
        result.append(line[pos:])
    return result

def encrypt_file(srcfilename, destfilename, key, chunksize=64*1024):
    """ 
    encrypts a file using AES with a given key
    Parameters:
    - srcfilename
      name of the file to encrypt
    - destfilename
      name of the destination file
    - key
      encryption key. The encryption key must be 16, 24 or 32
      bytes long.
    - chunksize
      size of the chunks to read and encrypt the file
    """
    rlist = []
    for i in range(16):
        rlist.append(chr(random.randint(0, 255)))
    iv = "".join(rlist)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(srcfilename)
    srcfile = open(srcfilename, "rb")
    destfile = open(destfilename, "wb")
    destfile.write(struct.pack('<Q', filesize))
    destfile.write(iv)
    while True:
        chunk = srcfile.read(chunksize)
        if len(chunk) == 0:
            break
        elif len(chunk) % 16 != 0:
            chunk += ' ' * (16 - len(chunk) % 16)
        destfile.write(encryptor.encrypt(chunk))
    srcfile.close()
    destfile.close()

def decrypt_file(srcfilename, destfilename, key, chunksize=64*1024):
    """
    decrypt a file using AES with a given key
    Parameters:
    - srcfilename
      name of the file to decrypt
    - destfilename
      name of the destination file
    - key
      encryption key. The encryption key must be 16, 24 or 32
      bytes long.
    - chunksize
      size of the chunks to read and encrypt the file
    """
    srcfile = open(srcfilename, "rb")
    origsize = struct.unpack('<Q', srcfile.read(struct.calcsize('Q')))[0]
    iv = srcfile.read(16)
    decryptor = AES.new(key, AES.MODE_CBC, iv)
    destfile = open(destfilename, "wb")
    while True:
        chunk = srcfile.read(chunksize)
        if len(chunk) == 0:
            break
        destfile.write(decryptor.decrypt(chunk))
    destfile.truncate(origsize)
    srcfile.close()
    destfile.close()

STATE_UPLOADED = "u"
STATE_DELETED = "d"

class CryptStoreEntry(object):
    """
    manages information about a file stored
    """

    def __init__(self, filepath, timestamp, state, entry_id):
        """
        creates an instance
        Parameters:
        - filepath
          relative file path
        - timestamp
          timestamp of the file
        - state
          state of the file
        - entry id
          unique id
        """
        self._filepath = filepath
        self._timestamp = timestamp
        self._state = state
        self._entry_id = entry_id

    def get_filepath(self):
        """
        Returns:
        - relative filepath
        """
        return self._filepath

    def get_timestamp(self):
        """
        Returns:
        - timestamp of the file
        """
        return self._timestamp

    def get_state(self):
        """
        Returns:
        - state of the file
        """
        return self._state

    def get_entry_id(self):
        """
        Returns:
        - unique id of the file
        """
        return self._entry_id

class CryptStore(object):
    """
    class to store encrypted files
    """

    def __init__(self, rootpath):
        """
        creates an instance
        Parameters:
        - rootpath
          root path of the store
        """
        self._config = CryptBoxConfig()
        self._rootpath = self._config.get_destination_directory()
        if self._rootpath == None or len(self._rootpath) == 0:
            show_error_message("No destination directory set.", True)
        if not os.path.isdir(self._rootpath):
            show_error_message("Destination directory not valid: %s" % self._rootpath, True)
        self._entries = []
        self._max_id = 1
        self._password = None
        self._password_hash = None
        self._load_password_hash()
        self._load_entries()

    def _load_entries(self):
        """
        loads the list of entries
        """
        pass

    def _save_entries(self):
        """
        saves the list of entries
        """
        pass

    def _load_password_hash(self):
        """
        loads the password hash
        """
        destination = self._rootpath
        fname = "cryptbox.0000000"
        filepath = os.path.join(destination, fname)
        try:
            hash_file = open(filepath, "r")
            self._password_hash = hash_file.read()
            hash_file.close()
        except IOError:
            self._password_hash = None
        pass

    def _save_password_hash(self):
        """
        saves the password hash
        """
        destination = self._root
        fname = "cryptbox.0000000"
        filepath = os.path.join(destination, fname)
        try:
            hash_file = open(filepath, "w")
            hash_file.write(self._password_hash)
            hash_file.close()
        except IOError:
            show_error_message("Unable to write %s." % filepath, True)

    def _load_entries(self):
        """
        loads the file entries
        """
        pass

    def _save_entries(self):
        """
        saves the file entries
        """
        tempname = NamedTemporaryFile().name
        # Create a JSON dictionary
        store_dict = {}
        store_dict["max_id"] = self._max_id
        entry_list = []
        for entry in self._entries:
            entry_dict = {}
            entry_dict["filepath"] = entry.get_filepath()
            entry_dict["timestamp"] = entry.get_timestamp()
            entry_dict["state"] = entry.get_state()
            entry_dict["entry_id"] = entry.get_entry_id()
            entry_list.append(entry_dict)
        store_dict["entries"] = entry_list
        line = json.dumps(store_dict)
        # Write JSON to temporary file
        try:
            tempfile = open(tempname, "w")
            tempfile.write(line)
            tempfile.close()
        except IOError:
            show_error_message("Unable to create temporary file %s." % tempname, True)
        # Copy encrypted temporary file to cryptstore
        key = self.get_key()
        fname = "cryptbox.0000001"
        destpath = os.path.join(self._rootpath, fname)
        encrypt_file(tempname, destpath, key)
        # Delete temporary file
        try:
            os.remove(tempname)
        except OSError:
            show_error_message("Unable to remove temporary file %s." % tempname)

    def has_password(self):
        """
        checks, if a password has been set
        Return:
        - True:  password has been checked
        - False: no password was set
        """
        return self._password_hash != None

    def check_password(self, password):
        """
        checks, if a password matches the password of the cryptstore
        Parameters:
        - True:  password matches
        - False: password doesn't match
        """
        result = False
        if self.has_password():
            m = hashlib.sha512()
            m.update(password)
            result = self._password_hash == m.hexdigest()
        return result

    def set_new_password(self, password):
        """
        sets a new password for the cryptstore
        Parameters:
        - password 
          new password to set
        """
        self._password = password
        m = hashlib.sha512()
        m.update(password)
        self._password_hash = m.hexdigest()
        self._save_password_hash()

    def get_key(self):
        """
        Return:
        - key to encrypt or decrypt files
        """
        if self._password == None:
            show_error_message("No passort set.", True)
        return normalize_key(self._password)

    def set_password(self, password):
        """
        sets the password to encrypt the file
        Parameters:
        - password
          password to set
        """
        if self.check_password(password):
            self._password = password

    def upload_file(self, fileinfo):
        """
        uploads a file to the store
        - fileinfo
          file info of the (local) file to upload
        """
        # upload the file
        # TODO: implement this
        # create an entry
        if self._password == None:
            show_error_message("No passwort set.", True)
        filepath = fileinfo.get_relative_path()
        timestamp = fileinfo.get_timestamp()
        state = STATE_UPLOADED
        entry_id = self._max_id
        self._max_id = self._max_id + 1
        entry = CryptStoreEntry(filepath, timestamp, state, entry_id)
        self._entries.append(entry)
        self._save_entries()

    def download_file(self, entry, destpath):
        if self._password == None:
            show_error_message("No passort set.", True)
        pass

    def delete_file(self, entry):
        pass
