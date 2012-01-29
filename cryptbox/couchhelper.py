# couchhelper - Helper classes to access CouchDB databases
#
# Copyright 2011 Jochen Skulj, jochen@jochenskulj.de
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

import hashlib
import httplib
import json

class CouchURI(object):
    """
    Helper class to create a URI
    """

    def __init__(self, endflag=False):
        """
        creates an instance
        Parameters:
        - endflag
          if True, the URI ends with a slash
        """
        self._endflag = endflag
        self._elements = []

    def get_element(self, index):
        """
        returns an element of the URI
        Parameters:
        - index
          index of an element
        Returns:
        - element or empty string
        """
        result = ""
        if  index >= 0 and index < len(self._elements):
            result = self._elements[index]
        return result

    def get_uri_string(self):
        """
        Returns:
        - URI as a string
        """
        stringlist = [ ]
        index = 0
        for element in self._elements:
            prev = self.get_element(index)
            if not prev.startswith("?"):
                stringlist.append("/")
            stringlist.append(element)
            index = index + 1
        if self._endflag:
            stringlist.append("/")
        return "".join(stringlist)

    def append(self, element, value=None):
        """
        appends an element or a variable to the URI
        Parameters:
        - element
          element or variable name
        - value
          optional variable name
        """
        newelement = element
        if value:
            newelement = "".join(["?", element, "=", value])
        self._elements.append(newelement)

class JSONResponse(object):
    """
    represents a JSON response
    """

    def __init__(self, response):
        """
        creates an instance
        Parameters:
        - response
          a http responsse
        """
        self._ok_flag = None
        self._error = None
        self._elements = None
        s = response.read()
        self._response_string = s[0:len(s) - 1]
        dump = json.loads(self._response_string)
        if type(dump) == dict:
            if dump.has_key("ok"):
                self._ok_flag = dump["ok"]
            if dump.has_key("error"):
                self._error = dump["error"]
        self._elements = dump

    def get_response_string(self):
        """
        Returns:
        - response as a string
        """
        return self._response_string

    def get_error(self):
        """
        Returns:
        - error in the response
        """
        return self._error

    def get_elements(self):
        """
        Returns:
        - list of elements
        """
        return self._elements

    def get_ok_flag(self):
        """
        Returns:
        - ok flag in the response
        """
        return self._ok_flag

class HttpHelper(object):
    """
    Helper class to support http communication
    """

    def __init__(self, host, port=5984):
        """
        creates an instance
        - host
          host to connect
        - port
          port to connect
        """
        self._host = host
        self._port = port

    def _connect(self):
        """
        connects to the server
        """
        return httplib.HTTPConnection(self._host, self._port)

    def get_host(self):
        """
        Returns:
        - host to connect
        """
        return self._host

    def get_port(self):
        """
        Returns:
        - port to connect
        """
        return self._port

    def get(self, uri):
        """
        invokes a get request
        Parameters:
        - uri
          URI to use
        Returns:
        - response of the request
        """
        c = self._connect()
        headers = {"Accept": "application/json"}
        c.request("GET", uri.get_uri_string(), None, headers)
        return JSONResponse(c.getresponse())

    def post(self, uri, body):
        """
        invokes a post request
        Parameters:
        - uri
          URI to use
        - body
          body to transfer
        Returns:
        - response of the request
        """
        c = self._connect()
        headers = {"Content-type": "application/json"}
        c.request('POST', uri.get_uri_string(), body, headers)
        return JSONResponse(c.getresponse())

    def put(self, uri, body):
        """
        invokes a put request
        Parameters:
        - uri
          URI to use
        - body
          body to transfer
        Returns:
        - response of the request
        """
        c = self._connect()
        if len(body) > 0:
            headers = {"Content-type": "application/json"}
            c.request("PUT", uri.get_uri_string(), body, headers)
        else:
            c.request("PUT", uri.get_uri_string(), body)
        return JSONResponse(c.getresponse())

    def delete(self, uri):
        """
        invokes a post request
        Parameters:
        - uri
          URI to use
        Returns:
        - response of the request
        """
        c = self._connect()
        c.request("DELETE", uri.get_uri_string())
        return JSONResponse(c.getresponse())

class CouchKey(object):
    """
    Helper class to generate Document IDs
    """

    def __init__(self, value_list):
        """
        creates an instance
        Parameters:
        - value_list
          list of values that are used to generate the key
        """
        m = hashlib.md5()
        for value in value_list:
            m.update(value)
        self._key = m.hexdigest()

    def get_key(self):
        """
        Returns:
        - the key
        """
        return self._key

class CouchDocument(object):
    """
    represents a CouchDB document
    """

    def __init__(self, doc_id):
        """
        creates an instance
        Parameters:
        - doc_id
          id of the document
        """
        self._doc_id = doc_id
        self._rev_id = None
        self._values = { }

    def set_rev_id(self, rev_id):
        """
        sets the revision id
        Parameters:
        - rev_id
          revision id to set
        """
        self._rev_id = rev_id

    def get_doc_id(self):
        """
        Returns:
        - id of the document
        """
        return self._doc_id

    def get_rev_id(self):
        """
        Returns:
        - revision id of the document
        """
        return self._rev_id

    def set_value(self, key, value):
        """
        sets a value of the document
        Parameters:
        - key
          key of the value
        - value
          value to set
        """
        self._values[key] = value

    def get_value(self, key):
        """
        returns the value to a given key
        Parameters:
        - key
          key to retrieve the value
        Returns:
        - value to the key
        """
        result = None
        if self._values.has_key(key):
            result = self._values[key]
        return result

    def get_values(self):
        """
        Returns:
        - dictionary of all values of the document
        """
        return self._values

    def dump_values(self):
        """
        dumps the values in a JSON document
        Returns:
        - Couch DB document in JSON
        """
        dump_dict = { }
        if self._rev_id:
            dump_dict["_rev"] = self._rev_id
        dump_dict["value"] = self._values
        dump_doc = json.dumps(dump_dict)
        return dump_doc

    def load(self, response):
        """
        loads a document from a JSON response
        Parameters:
        - response
          JSON response to load the documend
        """
        self._doc_id = response.get_elements()["_id"]
        self._rev_id = response.get_elements()["_rev"]
        self._values = response.get_elements()["value"]

class CouchViewsDocument(object):
    """
    CouchDB design document to manage views
    """

    def __init__(self):
        """
        creates an instance
        """
        self._doc_id = "_design/_views"
        self._rev_id = None
        self._views = { }

    def set_rev_id(self, rev_id):
        """
        sets the revision id
        Parameters:
        - rev_id
          revision id to set
        """
        self._rev_id = rev_id

    def get_rev_id(self):
        """
        Returns:
        - revision in
        """
        return self._rev_id

    def get_views(self):
        """
        Returns:
        - list of views
        """
        return self._views.keys()

    def add_view(self, view_name, source):
        """
        adds a new view
        Parameters:
        - view_name
          name of the view
        - source
          view source
        """
        self._views[view_name] = source

    def dump(self):
        """
        dumps the views in a JSON document
        Returns:
        - Couch DB document in JSON
        """
        dump_dict = { }
        dump_dict["_id"] = self._doc_id
        if self._rev_id:
            dump_dict["_rev"] = self._rev_id
        views_dict = { }
        for view_name in self._views.keys():
            source = self._views[view_name]
            entry_dict = {}
            entry_dict["map"] = source
            views_dict[view_name] = entry_dict
        dump_dict["views"] = views_dict
        dump_doc = json.dumps(dump_dict)
        return dump_doc

    def load(self, response):
        """
        loads a document from a JSON response
        Parameters:
        - response
          JSON response to load the documend
        """
        self._doc_id = response.get_elements()["_id"]
        self._rev_id = response.get_elements()["_rev"]
        view_dict = response.get_elements()["views"]
        self._views.clear()
        for view_name in view_dict.keys():
            entry_dict = view_dict[view_name]
            source = entry_dict["map"]
            self._views[view_name] = source

class CouchDatabase(object):
    """
    Helper class to access CouchDB databases
    """
    
    def __init__(self, name=None, host="127.0.0.1", port="5984"):
        """
        creates an instance
        Parameters:
        - name
          name of the database
        - host
          host to use
        - port
          port to use
        """
        self._name = name
        self._http_helper = HttpHelper(host, port)
        if self._name:
            if not self._name in self.get_databases():
                flag = self.create_database()
                if not flag:
                    self._name = None

    def _load_views(self):
        """
        loads the design document containing view definitions
        Returns:
        - view design documents
        """
        result = None
        if self._name:
            result = CouchViewsDocument()
            uri = CouchURI()
            uri.append(self._name)
            uri.append("_design")
            uri.append("_views")
            response = self._http_helper.get(uri)
            if response.get_error() == None:
                result.load(response)
        return result
        
    def _save_views(self, view_doc):
        """
        saves or updates the design document containing view 
        definitions
        Paramaeters:
        - view_dov
          view design documents
        Returns:
        - True: view design document was saved
        - False: failed to save the view document
        """
        result = False
        if self._name:
            body = view_doc.dump()
            uri = CouchURI()
            uri.append(self._name)
            uri.append("_design")
            uri.append("_views")
            response = self._http_helper.put(uri, body)
            result = response.get_ok_flag()
            if result:
                rev_id = response.get_elements()["rev"]
                view_doc.set_rev_id(rev_id)
        return result

    def _delete_views(self):
        """
        deletes the design document containing view definitions
        Returns:
        - True: view design document was deleted
        - False: failed to delete the view design document
        """
        pass

    def get_name(self):
        """
        Returns:
        - name of the database
        """
        return self._name

    def get_databases(self):
        """
        Returns:
        - list of existing databases
        """
        uri = CouchURI()
        uri.append("_all_dbs")
        result = self._http_helper.get(uri).get_elements()
        return result

    def create_database(self):
        """
        creates the database
        Returns:
        - True: database successfully created.
        - False: database couldn't be created.
        """
        uri = CouchURI()
        uri.append(self._name)
        response = self._http_helper.put(uri, "")
        return response.get_ok_flag()

    def delete_database(self):
        """
        deletes the database
        Returns:
        - True: database successfully deleted.
        - False: database couldn't be deleted.
        """
        result = False
        if self._name:
            uri = CouchURI()
            uri.append(self._name)
            response = self._http_helper.delete(uri)
            result = response.get_ok_flag()
        return result

    def save_document(self, doc):
        """
        saves a document to the database
        Parameters:
        - doc
          CouchDocument to save
        Returns:
        - True: document was saved.
        - False: document wasn't saved.
        """
        result = False
        if self._name:
            uri = CouchURI()
            uri.append(self._name)
            body = None
            body = doc.dump_values()
            uri.append(doc.get_doc_id())
            response = self._http_helper.put(uri, body)
            result = response.get_ok_flag()
            if result:
                rev_id = response.get_elements()["rev"]
                doc.set_rev_id(rev_id)
        return result

    def load_document(self, doc_id):
        """
        loads a document from the database
        Parameters:
        - doc_id
          id of the document to load
        Returns:
        - document or None
        """
        result = None
        uri = CouchURI()
        uri.append(self._name)
        uri.append(doc_id)
        response = self._http_helper.get(uri)
        if response.get_error() == None:
            result = CouchDocument(doc_id)
            result.load(response)
        return result

    def delete_document(self, doc):
        """
        deletes a document in the database
        Parameters:
        - doc
          document to delete
        Returns:
        - True:  document was deleted 
        - False: document was not deleted
        """
        result = False
        uri = CouchURI()
        uri.append(self._name)
        uri.append(doc.get_doc_id())
        uri.append("rev", doc.get_rev_id())
        response = self._http_helper.delete(uri)
        if response.get_error() == None:
            result = True
        return result

    def get_document_list(self):
        """
        retrieves a list of all documents in the database
        Returns:
        - list containing the id of each document in the database
        """
        result = None
        uri = CouchURI()
        uri.append(self._name)
        uri.append("_all_docs")
        response = self._http_helper.get(uri)
        if response.get_error() == None:
            result = []
            rows = response.get_elements()["rows"]
            for row in rows:
                doc_id = row["id"]
                if not doc_id.startswith("_"):
                    result.append(doc_id)
        return result

    def add_view(self, view_name, view_source):
        """
        defines a new view in the database
        Parameters:
        - view_name
          name of the view
        - view_source
          source code of the view
        """
        view_doc = self._load_views()
        view_doc.add_view(view_name, view_source)
        self._save_views(view_doc)

    def get_view_list(self):
        """
        Returns:
        - list of views defined for the database
        """
        views_doc = self._load_views()
        return views_doc.get_views()

    def query_view(self, view_name):
        """
        queries a view
        Parameters:
        - view_name
          name of the view to query
        Returns:
        - list of query results
        """
        result = None
        if self._name:
            result = []
            uri = CouchURI()
            uri.append(self._name)
            uri.append("_design")
            uri.append("_views")
            uri.append("_view")
            uri.append(view_name)
            response = self._http_helper.get(uri)
            if response.get_error() == None:
                rows = response.get_elements()["rows"]
                for entry in rows:
                    result_entry = {}
                    result_entry["id"] = entry["id"]
                    result_entry["value"] = entry["value"]
                    result.append(result_entry)
        return result

