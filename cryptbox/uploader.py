# cryptbox - class to process uploads to the CryptStore
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

class Uploader(object):
    """
    class to process uploads to the CryptStore
    """

    def __init__(self, cryptstore):
        """
        creates an instance
        Parameters:
        - cryptstore
          CryptStore instance to use
        """
        self._cryptstore = cryptstore

    def run(self):
        """
        executes the Uploader
        """
        print "Uoloader.run()"
