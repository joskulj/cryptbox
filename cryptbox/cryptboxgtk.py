# cryptbox-gtk - GTK GUI classes for cryptbox
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

import keyring
import getpass
import gtk
import pygtk
import sys

from config import *

class ConfigWindow(object):
    """
    window to edit the cryptbox configuration
    """

    def __init__(self):
        """
        creates an instance
        """
        self._config = CryptBoxConfig()
        self._widget_tree = None
        self._window = None
        self._entry_source = None
        self._entry_destination = None
        self.init_widgets()

    def init_widgets(self):
        """
        initializes the widgets
        """
        builder = gtk.Builder()
        builder.add_from_file("config.glade")
        self._window = builder.get_object("config_window")
        self._entry_source = builder.get_object("entry_source")
        self._entry_destination = builder.get_object("entry_destination")
        self._window.show()
        dic = {"on_config_window_destroy" : self.on_config_window_destroy
                , "on_button_source_clicked" : self.on_button_source_clicked
                , "on_button_destination_clicked" : self.on_button_destination_clicked
                , "on_button_ok_clicked" : self.on_button_ok_clicked
                , "on_button_cancel_clicked" : self.on_button_cancel_clicked }
        builder.connect_signals(dic)
        if self._config.exists():
            if self._config.get_source_directory():
                self._entry_source.set_text(self._config.get_source_directory())
            if self._config.get_destination_directory():
                self._entry_destination.set_text(self._config.get_destination_directory())
 
    def show(self):
        """
        displays the window
        """
        self._window.show()

    def choose_folder(self):
        """
        opens a dialog to choose a folder
        Returns:
        - chosen folder or None if dialog was canceled
        """
        result = None
        title = "Choose folder"
        parent = self._window 
        action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                   gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        dialog = gtk.FileChooserDialog(title, parent, action, buttons)
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            result = dialog.get_filename()
        dialog.destroy()
        return result

    def on_config_window_destroy(self, widget):
        """
        handles the event to destroy the window
        Parameters:
        - widget
          widget that triggered the event
        """
        gtk.main_quit()

    def on_button_source_clicked(self, widget):
        """
        handles the event when the source button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        source = self.choose_folder()
        if source:
            self._entry_source.set_text(source)

    def on_button_destination_clicked(self, widget):
        """
        handles the event when the destination button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        destination = self.choose_folder()
        if destination:
            self._entry_destination.set_text(destination)

    def on_button_ok_clicked(self, widget):
        """
        handles the event when the OK button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        ok_flag = True
        source = self._entry_source.get_text()
        destination = self._entry_destination.get_text()
        save_flag = False
        if len(source) > 0:
            self._config.set_source_directory(source)
            save_flag = True
        else:
            self._config.set_source_directory(None)
        if len(destination) > 0:
            self._config.set_destination_directory(destination)
            save_flag = True
        else:
            self._config.set_destination_directory(None)
        if save_flag:
            self._config.save()
        if ok_flag:
            gtk.main_quit()

    def on_button_cancel_clicked(self, widget):
        """
        handles the event when the Cancel button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        gtk.main_quit()

class LoginWindow(object):
    """
    window to enter the (existing) password at the start of CryptBox
    """

    def __init__(self, cryptstore):
        """
        creates an instance
        Parameters:
        - cryptstore
          cryptstore to set the password
        """
        self._ok_flag = False
        self._cryptstore = cryptstore
        self._window = None
        self._entry_password = None
        self._check_keyring = None
        self.init_widgets()

    def is_ok(self):
        """
        checks, if login was successful
        Returns:
        - True:  login was successful
        - False: login was not successful
        """
        return self._ok_flag

    def init_widgets(self):
        """
        initializes the widgets
        """
        builder = gtk.Builder()
        builder.add_from_file("login.glade")
        self._window = builder.get_object("login_window")
        self._entry_password = builder.get_object("entry_password")
        self._check_keyring = builder.get_object("check_keyring")
        dic = {"on_login_window_destroy" : self.on_config_window_destroy
                , "on_button_ok_clicked" : self.on_button_ok_clicked
                , "on_button_cancel_clicked" : self.on_button_cancel_clicked }
        builder.connect_signals(dic)
        builder.get_object("login_button_ok").set_flags(gtk.CAN_DEFAULT)
        builder.get_object("login_button_ok").grab_default()

    def show(self):
        """
        displays the window
        """
        self._window.show()


    def on_config_window_destroy(self, widget):
        """
        handles the event to destroy the window
        Parameters:
        - widget
          widget that triggered the event
        """
        gtk.main_quit()

    def on_button_ok_clicked(self, widget):
        """
        handles the event when the OK button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        password = self._entry_password.get_text()
        if self._cryptstore.check_password(password):
            self._cryptstore.set_password(password)
            if self._check_keyring.get_active():
                user = getpass.getuser()
                keyring.set_password("cryptbox", user, password)
            self._ok_flag = True
            self._window.destroy()
            gtk.main_quit()
        else:
            md = gtk.MessageDialog(self._window, 
                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
                   gtk.BUTTONS_CLOSE, "Invalid password.")
            md.run()
            md.destroy()

    def on_button_cancel_clicked(self, widget):
        """
        handles the event when the Cancel button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        gtk.main_quit()

class NewPasswordWindow(object):
    """
    window to setup new password for cryptbox
    """

    def __init__(self):
        """
        creates a new instance
        """
        self._new_password = None
        self._window = None
        self._entry_new_password = None
        self._entry_repeat_password = None
        self.init_widgets()

    def get_new_password(self):
        """
        Return:
        - new password or None, if no new password has set up
        """
        return self._new_password

    def init_widgets(self):
        """
        initializes the widgets
        """
        builder = gtk.Builder()
        builder.add_from_file("password.glade")
        self._window = builder.get_object("new_password_window")
        self._entry_new_password = builder.get_object("entry_new_password")
        self._entry_repeat_password = builder.get_object("entry_repeat_password")
        dic = {"on_new_password_window_destroy" : self.on_config_window_destroy
                , "on_button_ok_clicked" : self.on_button_ok_clicked
                , "on_button_cancel_clicked" : self.on_button_cancel_clicked }
        builder.connect_signals(dic)
        builder.get_object("password_button_ok").set_flags(gtk.CAN_DEFAULT)
        builder.get_object("password_button_ok").grab_default()

    def show(self):
        """
        displays the window
        """
        self._window.show()


    def on_config_window_destroy(self, widget):
        """
        handles the event to destroy the window
        Parameters:
        - widget
          widget that triggered the event
        """
        gtk.main_quit()

    def on_button_ok_clicked(self, widget):
        """
        handles the event when the OK button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        password = self._entry_new_password.get_text()
        repeat = self._entry_repeat_password.get_text()
        if password != repeat:
            md = gtk.MessageDialog(self._window, 
                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
                   gtk.BUTTONS_CLOSE, "Entered passwords do not match.")
            md.run()
            md.destroy()
            return
        if len(password) < 6:
            md = gtk.MessageDialog(self._window, 
                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
                   gtk.BUTTONS_CLOSE, "Password is too short.")
            md.run()
            md.destroy()
            return
        self._new_password = password
        gtk.main_quit()

    def on_button_cancel_clicked(self, widget):
        """
        handles the event when the Cancel button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        gtk.main_quit()


def show_config_window():
    """
    shows the configuration dialog
    """
    window = ConfigWindow()
    window.show()
    gtk.main()

def show_login_window(cryptstore):
    """
    shows the login window
    Parameters:
    - cryptstore
      cryptstore to login
    Returns:
    - True:  login was successful
    - False: login was not successful
    """
    result = False
    user = getpass.getuser()
    password = keyring.get_password("cryptbox", user)
    if password:
         if cryptstore.check_password(password):
            cryptstore.set_password(password)
            result = True
    if not result:
        window = LoginWindow(cryptstore)
        window.show()
        gtk.main()
        result = window.is_ok()
    return result

def show_new_password_window():
    """
    shows the window to set up a new password
    Returns:
    - new password or None
    """
    window = NewPasswordWindow()
    window.show()
    gtk.main()
    return window.get_new_password()

def show_error_message(message, exit=False):
    """
    displays an error message
    Parameters:
    - message
      error message to display
    - exit
      flag, if the application should terminate
    """
    print "Error: %s" % message
    # TODO: implement GTK dialog
    if exit:
        sys.exit(-1)


if __name__ == "__main__":
    import cryptstore
    print show_new_password_window()
