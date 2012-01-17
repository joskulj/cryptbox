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

class ConfigWindow(object):
    """
    window to edit the cryptbox configuration
    """

    def __init__(self):
        """
        creates an instance
        """
        self._running = False
        self._widget_tree = None
        self._window = None
        self.init_widget_tree()

    def init_widget_tree(self):
        """
        initializes the widget tree
        """
        gladefile = "cryptbox.glade"
        windowname = "config_window"
        self._widget_tree = gtk.glade.XML(gladefile, windowname)
        self._window = self._widget_tree.get_widget(windowname)
        dic = {"on_config_window_destroy" : self.on_config_window_destroy
                , "on_source_button_clicked" : self.on_source_button_clicked
                , "on_destination_button_clicked" : self.on_destination_button_clicked
                , "on_ok_button_clicked" : self.on_ok_button_clicked
                , "on_cancel_button_clicked" : self.on_cancel_button_clicked }
        self._widget_tree.signal_autoconnect(dic)
 
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

    def on_source_button_clicked(self, widget):
        """
        handles the event when the source button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        print "on_source_button_clicked"

    def on_destination_button_clicked(self, widget):
        """
        handles the event when the destination button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        print "on_destination_button_clicked"

    def on_ok_button_clicked(self, widget):
        """
        handles the event when the OK button is clicked
        Parameters:
        - widget
          widget that triggered the event
        """
        print "on_ok_button_clicked"

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

if __name__ == "__main__":
   show_config_window()
