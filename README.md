# cryptbox

Version 0.1

Jochen Skulj, jochen@jochenskulj.de

## Basic idea

There are a lot solutions to share files among different computers. You 
can use removable media, set up an own server or use cloud services
like DropBox or UbuntuOne. Using cloud services is probably the easiest
approach since it is easy to set up, easy to use and cheap - if not
even free at all.

But are they secure? Can you use these services to share personal
documents or private data? Of course, all service providers claim to
be secure and to encrypt your date. But since in most cases you
don't know how your data is encrypted, where the data will be stored
and how the keys to decrypt your data are managed, it seems to be
a little risky to trust these providers entirely.

The only advisable way to usage cloud storage services is to encrypt
your data locally on your computer before it is transmitted to the
cloud. *cryptbox* is designed to be an easy to use tool that enables
everyone to encrypt personal to use cloud services in a more secury
way.

*cryptbox* is a GTK-based application for GNU/Linux written in Python.
It synchronizes the files from a given *source directory* with a
*destination directory*. During the synchronization processes the
files are automatically encrypted and decrypted. Encryption is
implemented by using AES.

With *cryptbox* you can locate the *destination directory* in a 
directory that is shared by a cloud service and place the files, you 
want to share in your *source directory*. By using *cryptbox* in this
way you can use cloud services with your own encryption.

## Requirements

*cryptbox* is a Python application designed to run under GNU/Linux and
GNOME. it uses *Couch DB* and *python-keyring*. On Debian-based systems
you should execute

    sudo apt-get install couchdb python-keyring

to install the required packages.

## Installation

**Important note:** *cryptbox* is currently in an early development
stage. Don't use it in critical environments. If you like the approach
of *cryptbox* or want to comment, just give me some feedback via e-mail.

Use following commands to download *cryptbox* from the Git repository
and install it:

    git clone https://github.com/joskulj/cryptbox.git
    cd cryptbox
    sudo python setup.py install

## Usage

To start *cryptbox* execute:

    cryptbox-runner --start

If you start *cryptbox* for the first time, you have to set up
a new password. A dialog opens that asks you to enter and
repeat the new password. Please note that currently there is
no option to change the password. This feature will be implemented
in the future.

After the password is set you have
to enter the password each time *cryptbox* is started. You
have the option to store the password in your keyring, so you
can start *cryptbox* without any user interaction.

*cryptbbox* is designed to run as a background task. Therefore
it is recommended tp set up *cryptbox* as a start up application
using *gnome-session-properties*.

While *cryptbox* is runnoing, *source* and *destination diretory* are
synchronized each 10 seconds. The actions performed by *cryptbox* are
logged in

    ~/.cryptbox.log

Please note that the log file is written with some delay. To watch the
complete log file you should stop *cryptbox*.

You can stop *cryptbox* with following command:

    cryptbox-runner --stop
