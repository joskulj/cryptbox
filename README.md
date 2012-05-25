# cryptbox

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
*destination directory*. 

This repo contains dotfiles for

- zsh
- vim/gvim

## Usage

    git clone https://github.com/joskulj/dotfiles.git ~/dotfiles
    cd ~/dotfiles
    ./install.sh
