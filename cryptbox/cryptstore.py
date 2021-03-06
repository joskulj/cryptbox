# -*- coding: iso-8859-15 -*-

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
import time

from Crypto.Cipher import AES
from tempfile import *

from config import *
from fileinfo import *

from debug import *

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

def adjust_time(srcfilename, destfilename):
    """
    sets atime and mtime of a destination file corresponding to a
    source file
    Parameters:
    - srcfilename
      name of the source file
    - destfilename
      name of the destination file
    """
    atime = os.path.getatime(srcfilename)
    mtime = os.path.getmtime(srcfilename)
    os.utime(destfilename, (atime, mtime))

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
    adjust_time(srcfilename, destfilename)

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
    adjust_time(srcfilename, destfilename)

def create_path(filepath):
    """
    checks, if a given filepath exists, and creates the path
    if it doesn't exists.
    Parameters:
    - filepath
      filepath to check
    Returns:
    - filepath was successfully checked or created
    """
    result = True
    dir_list = filepath.split("/")
    test_path = "/"
    for index in range(0, len(dir_list) - 1):
        test_path = os.path.join(test_path, dir_list[index])
        if len(test_path) > 1:
            if not os.path.exists(test_path):
                try:
                    os.mkdir(test_path)
                except OSError:
                    result = False
    return result

# STATE_UPLOADED = "u"
# STATE_DELETED = "d"

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

    def set_state(self, state):
        """
        sets the state
        Parameters:
        - state
          state to set
        """
        self._state = state

    def set_timestamp(self, timestamp):
        """
        sets the timestamp
        Parameters:
        - timestamp
          timestamp to set
        """
        self._timestamp = timestamp

    def delete_file(self, timestamp):
        """
        deletes the corresponding file
        Parameters:
        - timestamp
          timestamp for deleting files
        Returns:
        - True:  file was deleted
        - False: deleting file failed
        """
        flag = True
        config = CryptBoxConfig()
        rootpath = config.get_destination_directory()
        filepath = os.path.join(rootpath, self._filepath)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                flag = False
        if flag:
            self._timestamp = timestamp
            self._state = FILEINFO_STATE_DELETED
        return flag

class CryptStore(object):
    """
    class to store encrypted files
    """

    def __init__(self):
        """
        creates an instance
        """
        self._config = CryptBoxConfig()
        self._rootpath = self._config.get_destination_directory()
        if self._rootpath == None or len(self._rootpath) == 0:
            show_error_message("No destination directory set.", True)
        if not os.path.isdir(self._rootpath):
            show_error_message("Destination directory not valid: %s" % self._rootpath, True)
        self._entries = []
        self._entry_dict = {}
        self._max_id = 2
        self._password = None
        self._password_hash = None
        self._password_timestamp = None
        self._load_password_hash()

    def refresh(self):
        """
        reloads the entries
        """
        self._entries = []
        self._entry_dict = {}
        self._max_id = 2
        self._load_entries() 

    def _load_password_hash(self):
        """
        loads the password hash
        """
        destination = self._rootpath
        fname = "cryptbox.00000000"
        filepath = os.path.join(destination, fname)
        try:
            hash_file = open(filepath, "r")
            self._password_hash = hash_file.read()
            hash_file.close()
        except IOError:
            self._password_hash = None
        if self._password_hash:
            try:
                self._password_timestamp = os.path.getmtime(filepath)
            except:
                self._password_timestamp = None

    def _save_password_hash(self):
        """
        saves the password hash
        """
        destination = self._rootpath
        fname = "cryptbox.00000000"
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
        # decrypt entries file to a temporary file
        key = self.get_key()
        fname = "cryptbox.00000001"
        srcpath = os.path.join(self._rootpath, fname)
        if not os.path.isfile(srcpath):
            # entry file does not exist
            return
        tempname = NamedTemporaryFile().name
        decrypt_file(srcpath, tempname, key)
        # read decrypted file
        line = None
        try:
            tempfile = open(tempname, "r")
            line = tempfile.readline()
            tempfile.close()
        except IOError:
            show_error_message("Unable to read temporary file %s." % tempname, True)
        # parse JSON content
        try:
            store_dict = json.loads(line)
            if type(store_dict) == dict:
                self._max_id = store_dict["max_id"]
                entry_list = store_dict["entries"]
                self._entries = []
                self._entry_dict = {}
                for entry_dict in entry_list:
                    filepath = entry_dict["filepath"]
                    timestamp = entry_dict["timestamp"]
                    state = entry_dict["state"]
                    entry_id = entry_dict["entry_id"]
                    entry = CryptStoreEntry(filepath, timestamp, state, entry_id)
                    self._entries.append(entry)
                    self._entry_dict[unicode(filepath)] = entry
        except ValueError:
            show_error_message("Unable to parse entry file.", False)
        # delete temporary file
        try:
            os.remove(tempname)
        except OSError:
            show_error_message("Unable to remove temporary file %s." % tempname)

    def _get_password_hash(self, password):
        """
        computes a hash for a given password
        Parameters:
        - password
        Returns:
        - hash of the password
        """
        result = None
        m1 = hashlib.sha512()
        salt = self._config.get_password_salt()
        if salt != None:
            m1.update(password + salt)
        else:
            m1.update(password)
        result = m1.hexdigest()
        repeat_index = 0
        repeat_max = self._config.get_password_repeat_hash()
        while repeat_index < repeat_max:
            m2 = hashlib.sha512()
            m2.update(result)
            result = m2.hexdigest()
            repeat_index += 1
        return result
 
    def _save_entries(self):
        """
        saves the file entries
        """
        tempname = NamedTemporaryFile().name
        # create a JSON dictionary
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
        # crite JSON to temporary file
        try:
            tempfile = open(tempname, "w")
            tempfile.write(line)
            tempfile.close()
        except IOError:
            show_error_message("Unable to create temporary file %s." % tempname, True)
        # copy encrypted temporary file to cryptstore
        key = self.get_key()
        fname = "cryptbox.00000001"
        destpath = os.path.join(self._rootpath, fname)
        encrypt_file(tempname, destpath, key)
        # delete temporary file
        try:
            os.remove(tempname)
        except OSError:
            show_error_message("Unable to remove temporary file %s." % tempname)

    def get_entry(self, filepath):
        """
        gets an entry by the path of the file
        Parameters:
        - filepath
          path of a file
        Returns:
        - corresponding file entry
        """
        result = None
        if filepath in self._entry_dict.keys():
            result = self._entry_dict[unicode(filepath)]
        return result

    def get_entries(self):
        """
        Returns:
        - list of CryptStoreEntry instances
        """
        return self._entries

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
            if self._get_password_hash(password) == self._password_hash:
                result = True
        return result

    def check_password_timestamp(self):
        """
        checks if the password was changed since the password was
        loaded
        Returns:
        - True:  existing password is still valid
        - False: password was changed
        """
        result = True
        destination = self._rootpath
        fname = "cryptbox.00000000"
        filepath = os.path.join(destination, fname)
        try:
            timestamp = os.path.getmtime(filepath)
            if timestamp > self._password_timestamp:
                result = False
        except:
            result = False
        return result

    def set_new_password(self, password, load_entries=True):
        """
        sets a new password for the cryptstore
        Parameters:
        - password 
          new password to set
        - load_entries
          flag, if entries should be loaded
        """
        self._password = password
        self._password_hash = self._get_password_hash(self._password)
        self._save_password_hash()
        if load_entries:
            self._load_entries()

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
            self._load_entries()

    def upload_file(self, fileinfo):
        """
        uploads a file to the store
        - fileinfo
          file info of the (local) file to upload
        """
        # create an entry
        if self._password == None:
            show_error_message("No passwort set.", True)
        # set entry information
        filepath = fileinfo.get_relative_path()
        timestamp = fileinfo.get_file_timestamp() 
        state = FILEINFO_STATE_UPLOADED
        # check, if entry already exists
        entry = None
        if filepath in self._entry_dict.keys():
            entry = self._entry_dict[unicode(filepath)]
            entry_id = entry.get_entry_id()
        else:
            entry_id = self._max_id
            self._max_id = self._max_id + 1
        # upload the encrypted file
        srcpath = fileinfo.get_absolute_path()
        destname = "cryptbox.%08i" % entry_id
        destpath = os.path.join(self._rootpath, destname)
        encrypt_file(srcpath, destpath, self.get_key())
        # update entry information
        if entry == None:
            entry = CryptStoreEntry(filepath, timestamp, state, entry_id)
            self._entries.append(entry)
            self._entry_dict[unicode(filepath)] = entry
        else:
            entry.set_timestamp(timestamp)
            entry.set_state(state)
        self._save_entries()
        # update file info
        fileinfo.update_state(state, timestamp)

    def download_file(self, entry, rootpath):
        """
        downloads a file
        Parameters:
        - entry
          entry that identifies the file to download
        - destroot
          root path of the destination to copy the file to
        """
        if self._password == None:
            show_error_message("No passort set.", True)
        # create source path
        entry_id = entry.get_entry_id()
        srcname = "cryptbox.%08i" % entry_id
        srcpath = os.path.join(self._rootpath, srcname)
        # create destination path
        destpath = os.path.join(rootpath, entry.get_filepath())
        # download the file
        flag = create_path(destpath)
        if not flag:
            show_error_message("Unable to create directory path %s." % destpath, True)
        decrypt_file(srcpath, destpath, self.get_key())
        # update file info
        fileinfo = FileInfo(rootpath, destpath)
        timestamp = time.time()
        state = FILEINFO_STATE_DOWNLOADED
        fileinfo.update_state(state, timestamp)

    def delete_file(self, entry):
        """
        deletes a file
        Parameters:
        - entry
          entry that identifies the file to delete
        """
        flag = entry.delete_file(time.time())
        if flag:
            self._save_entries()

    def purge(self):
        """
        deletes all files that are marked as deleted
        Returns:
        - list of filepath that were purged
        """
        result = []
        index = 0
        while index < len(self._entries):
            entry = self._entries[index]
            if entry.get_state() == FILEINFO_STATE_DELETED: 
                entry_path = entry.get_filepath()
                success = True
                # create full file path
                entry_id = entry.get_entry_id()
                filename = "cryptbox.%08i" % entry_id
                filepath = os.path.join(self._rootpath, filename)
                # delete file
                try:
                    os.remove(filepath)
                except OSError:
                    show_error_message("Unable to delete %s." % filepath)
                    success = False
                if success:
                    # remove meta infomation
                    del self._entries[index]
                    del self._entry_dict[unicode(entry_path)]
                    result.append(entry_path)
            else:
                index += 1
        if len(result) > 0:
            self._save_entries()
        return result

