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

    def show(self):
        """
        displays the window
        """
        self._window.show()

def show_config_window():
    """
    shows the configuration dialog
    """
    window = ConfigWindow()
    window.show()
    gtk.main()

if __name__ == "__main__":
    show_config_window()
