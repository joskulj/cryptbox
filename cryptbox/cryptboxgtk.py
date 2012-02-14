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

import gtk
import gtk.glade
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
        self._source_entry = None
        self._destination_entry = None
        self.init_widget_tree()

    def init_widget_tree(self):
        """
        initializes the widget tree
        """
        gladefile = "cryptbox.glade"
        windowname = "config_window"
        self._widget_tree = gtk.glade.XML(gladefile, windowname)
        self._window = self._widget_tree.get_widget(windowname)
        self._source_entry = self._widget_tree.get_widget("source_entry")
        self._destination_entry = self._widget_tree.get_widget("destination_entry")
        dic = {"on_config_window_destroy" : self.on_config_window_destroy
                , "on_source_button_clicked" : self.on_source_button_clicked
                , "on_destination_button_clicked" : self.on_destination_button_clicked
                , "on_ok_button_clicked" : self.on_ok_button_clicked
                , "on_cancel_button_clicked" : self.on_cancel_button_clicked }
        self._widget_tree.signal_autoconnect(dic)
        if self._config.exists():
            if self._config.get_source_directory():
                self._source_entry.set_text(self._config.get_source_directory())
            if self._config.get_destination_directory():
                self._destination_entry.set_text(self._config.get_destination_directory())
 
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

    def on_source_button_clicked(self, widget):
        """
        handles the event when the source button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        source = self.choose_folder()
        if source:
            self._source_entry.set_text(source)

    def on_destination_button_clicked(self, widget):
        """
        handles the event when the destination button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        destination = self.choose_folder()
        if destination:
            self._destination_entry.set_text(destination)

    def on_ok_button_clicked(self, widget):
        """
        handles the event when the OK button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        ok_flag = True
        source = self._source_entry.get_text()
        destination = self._destination_entry.get_text()
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

    def on_cancel_button_clicked(self, widget):
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
   show_config_window()
