
cryptbox - Version 0.1.0

Copyright 2012, Jochen Skulj, jochen@jochenskulj.de
Published under GNU General Public License

ToDo
====
- Implement python setup
- Implement a proper logging
- optimize download and upload

Installation
============

Cryptbox uses CouchDB to manage file information. To install CouchDB
on Debian systems execute:

    sudo apt-get install couchdb

Setup/installation is not implemented yet. For testing cryptbox you have to
execute cryptbox/cryptbox.py directly.

Overview
========

Please note: Cryptbox is in a very early development state and is
considered to be experimental. It should not be used in productive
environments or to syncronize private or personal files. However,
if you like the idea and the approach of Cryptbox, you can give me
some feedback.

Cryptbox will syncronize files from a source directory with a destination
directory. The syncronized files in the destination file will be
encrypted. Cryptbox will be implemented as a daemon service that
syncronizes the files. The idea behind that application is to share
the encrypted files in the destination directory by using a service
like Dropbox.

Before you can use Cryptbox you have to configure the source and the
destination directory. To configure Cryptbox you have to execute

  cryptbox.py --config

A dialog will open that allows you to setup the source directory and
the destination directory.

Once Cryptbox is configured you can start and stop Cryptbox by following
commands:

  cryptbox.py --start
  cryptbox.py --stop

When you start Cryptbox for the first time you have to enter and
repeat a password that will be used to encrypt the files. Please note
that currently no option to change the password is available. Such
a feature will be implemented in the feature.

You have to enter the password each time you start Cryptbox. Alternatively
you have the option to save the password in your keyring.
