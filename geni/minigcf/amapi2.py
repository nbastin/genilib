# Copyright (c) 2015-2020  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Streamlined implementation of xmlrpc calls to AM API v2-compliant aggregates
# Only uses python requests module, without a ton of extra SSL dependencies

from __future__ import absolute_import

from six.moves import xmlrpc_client as xmlrpclib

from .util import _rpcpost

# pylint: disable=unsubscriptable-object
def getversion (url, root_bundle, cert, key, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((options,), methodname="GetVersion")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def listresources (url, root_bundle, cert, key, cred_strings, options = None, sliceurn = None):
  if not options: options = {}
  opts = {"geni_rspec_version" : {"version" : "3", "type" : "GENI"},
          "geni_available" : False,
          "geni_compressed" : False}

  if sliceurn:
    opts["geni_slice_urn"] = sliceurn

  # Allow all options to be overridden by the caller
  opts.update(options)

  req_data = xmlrpclib.dumps((cred_strings, opts), methodname="ListResources")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def deletesliver (url, root_bundle, cert, key, creds, slice_urn, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((slice_urn, creds, options), methodname="DeleteSliver")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def sliverstatus (url, root_bundle, cert, key, creds, slice_urn, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((slice_urn, creds, options), methodname="SliverStatus")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def renewsliver (url, root_bundle, cert, key, creds, slice_urn, date, options = None):
  FMT = "%Y-%m-%dT%H:%M:%S+00:00"
  if not options: options = {}
  req_data = xmlrpclib.dumps((slice_urn, creds, date.strftime(FMT), options), methodname="RenewSliver")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def listimages (url, root_bundle, cert, key, cred_strings, owner_urn, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((owner_urn, cred_strings, options), methodname="ListImages")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def createsliver (url, root_bundle, cert, key, creds, slice_urn, rspec, users, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((slice_urn, creds, rspec, users, options), methodname="CreateSliver")
  return _rpcpost(url, req_data, (cert, key), root_bundle)
