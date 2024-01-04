# Copyright (c) 2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# XML-RPC bindings for Protogeni CH/SA API revision 1

from __future__ import absolute_import

from six.moves import xmlrpc_client as xmlrpclib

from .util import _rpcpost

def ListComponents(url, root_bundle, cert, key, cred):
  req_data = xmlrpclib.dumps(({"credential" : cred},), methodname="ListComponents")
  return _rpcpost(url, req_data, (cert,key), root_bundle)

def GetCredential(url, root_bundle, cert, key, urn = None, uuid = None):
  if urn:
    req_data = xmlrpclib.dumps(({"urn" : urn, "type" : "Slice"},), methodname="GetCredential")
  elif uuid:
    req_data = xmlrpclib.dumps(({"uuid" : uuid, "type" : "Slice"},), methodname="GetCredential")
  else:
    req_data = xmlrpclib.dumps(tuple(), methodname="GetCredential")
  return _rpcpost(url, req_data, (cert,key), root_bundle)

def GetVersion(url, root_bundle, cert, key):
  req_data = xmlrpclib.dumps(tuple(), methodname="GetVersion")
  return _rpcpost(url, req_data, (cert,key), root_bundle)

def Resolve(url, root_bundle, cert, key, cred, urn, typ):
  obj = {"credential" : cred, "urn" : urn, "type" : typ}
  req_data = xmlrpclib.dumps((obj,), methodname="Resolve")
  return _rpcpost(url, req_data, (cert,key), root_bundle)

def Register(url, root_bundle, cert, key, user_cred, hrn):
  obj = {"credential" : user_cred, "hrn" : hrn, "type" : "Slice"}
  req_data = xmlrpclib.dumps((obj,), methodname="Register")
  return _rpcpost(url, req_data, (cert,key), root_bundle)
