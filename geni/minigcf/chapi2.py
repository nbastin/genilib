# Copyright (c) 2015-2020  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from six.moves import xmlrpc_client as xmlrpclib

from ..constants import SLICE_ROLE, PROJECT_ROLE, REQCTX, REQSTATUS
from .util import _rpcpost

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"

# pylint: disable=unsubscriptable-object
def _lookup (url, root_bundle, cert, key, typ, cred_strings, options):
  req_data = xmlrpclib.dumps((typ, cred_strings, options), methodname="lookup")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def get_version (url, root_bundle, cert, key, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps(tuple(), methodname = "get_version")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def lookup_key_info (url, root_bundle, cert, key, cred_strings, user_urn):
  options = {"match" : {"KEY_MEMBER" : user_urn} }
  return _lookup(url, root_bundle, cert, key, "KEY", cred_strings, options)

def lookup_service_info (url, root_bundle, cert, key, cred_strings, service_type):
  options = {"match" : {"SERVICE_TYPE" : service_type} }
  return _lookup(url, root_bundle, cert, key, "SERVICE", cred_strings, options)

def lookup_member_info (url, root_bundle, cert, key, cred_strings, urn = None, uid = None,
                        email = None, lastname = None):
  match = {}
  if urn: match["MEMBER_URN"] = urn
  if uid: match["MEMBER_UID"] = uid
  if email: match["MEMBER_EMAIL"] = email
  if lastname: match["MEMBER_LASTNAME"] = lastname
  options = {"match" : match}

  return _lookup(url, root_bundle, cert, key, "MEMBER", cred_strings, options)

def create_key_info (url, root_bundle, cert, key, cred_strings, data):
  req_data = xmlrpclib.dumps(("KEY", cred_strings, {"fields" : data}), methodname="create")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def get_credentials (url, root_bundle, cert, key, creds, target_urn):
  req_data = xmlrpclib.dumps((target_urn, creds, {}), methodname="get_credentials")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def create_slice (url, root_bundle, cert, key, cred_strings, name, proj_urn, exp = None, desc = None):
  fields = {}
  fields["SLICE_NAME"] = name
  if proj_urn: fields["SLICE_PROJECT_URN"] = proj_urn
  if exp: fields["SLICE_EXPIRATION"] = exp.strftime(DATE_FMT)
  if desc: fields["SLICE_DESCRIPTION"] = desc

  req_data = xmlrpclib.dumps(("SLICE", cred_strings, {"fields" : fields}), methodname = "create")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def update_slice (url, root_bundle, cert, key, cred_strings, slice_urn, fields):
  req_data = xmlrpclib.dumps(("SLICE", slice_urn, cred_strings, {"fields" : fields}), methodname = "update")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def lookup_slices_for_member (url, root_bundle, cert, key, cred_strings, member_urn):
  options = {}
  req_data = xmlrpclib.dumps(("SLICE", member_urn, cred_strings, options), methodname = "lookup_for_member")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def lookup_slices_for_project (url, root_bundle, cert, key, cred_strings, project_urn):
  options = {"match" : {"SLICE_PROJECT_URN" : project_urn} }
  return _lookup(url, root_bundle, cert, key, "SLICE", cred_strings, options)

def lookup_slice_members (url, root_bundle, cert, key, cred_strings, slice_urn):
  options = {}
  req_data = xmlrpclib.dumps(("SLICE", slice_urn, cred_strings, options), methodname = "lookup_members")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def create_project (url, root_bundle, cert, key, cred_strings, name, exp, desc = None):
  fields = {}
  fields["PROJECT_EXPIRATION"] = exp.strftime(DATE_FMT)
  fields["PROJECT_NAME"] = name
  if desc is not None:
    fields["PROJECT_DESCRIPTION"] = desc

  req_data = xmlrpclib.dumps(("PROJECT", cred_strings, {"fields" : fields}), methodname = "create")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def delete_project (url, root_bundle, cert, key, cred_strings, project_urn):
  """Delete project by URN
  .. note::
    You may or may not be able to delete projects as a matter of policy for the given authority."""

  options = {}

  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "delete")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

#def _update_project (url, root_bundle, cert, key, cred_strings, project_urn):
#  options = {"fields" : {}}
#  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "update")
#  s = requests.Session()
#  s.mount(url, GCU.TLSHttpAdapter())
#  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
#  return xmlrpclib.loads(resp.content)[0][0]


def lookup_projects (url, root_bundle, cert, key, cred_strings, urn = None, uid = None, expired = None):
  options = { }
  match = { }
  if urn is not None:
    match["PROJECT_URN"] = urn
  if uid is not None:
    match["PROJECT_UID"] = uid
  if expired is not None:
    match["PROJECT_EXPIRED"] = expired

  if match:
    options["match"] = match

  return _lookup(url, root_bundle, cert, key, "PROJECT", cred_strings, options)

def lookup_projects_for_member (url, root_bundle, cert, key, cred_strings, member_urn, expired = None):
  options = {}
  match = {}

  if expired is not None:
    match["PROJECT_EXPIRED"] = expired

  if match:
    options["match"] = match

  req_data = xmlrpclib.dumps(("PROJECT", member_urn, cred_strings, options), methodname = "lookup_for_member")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def lookup_project_members (url, root_bundle, cert, key, cred_strings, project_urn):
  options = {}

  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "lookup_members")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def lookup_aggregates (url, root_bundle, cert, key):
  options = {"match" : {'SERVICE_TYPE': 'AGGREGATE_MANAGER'}}

  return _lookup(url, root_bundle, cert, key, "SERVICE", [], options)


def modify_slice_membership (url, root_bundle, cert, key, cred_strings, slice_urn, add = None, remove = None, change = None):
  options = {}
  if add:
    to_add = []
    for urn,role in add:
      to_add.append({"SLICE_MEMBER" : urn, "SLICE_ROLE" : role})
    options["members_to_add"] = to_add
  if remove:
    options["members_to_remove"] = remove
  if change:
    to_change = []
    for urn,role in change:
      to_change.append({"SLICE_MEMBER" : urn, "SLICE_ROLE" : role})
    options["members_to_change"] = to_change

  req_data = xmlrpclib.dumps(("SLICE", slice_urn, cred_strings, options), methodname = "modify_membership")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def modify_project_membership (url, root_bundle, cert, key, cred_strings, project_urn, add = None, remove = None, change = None):
  options = {}
  if add:
    to_add = []
    for urn,role in add:
      to_add.append({"PROJECT_MEMBER" : urn, "PROJECT_ROLE" : role})
    options["members_to_add"] = to_add
  if remove:
    options["members_to_remove"] = remove
  if change:
    to_change = []
    for urn,role in change:
      to_change.append({"PROJECT_MEMBER" : urn, "PROJECT_ROLE" : role})
    options["members_to_change"] = to_change

  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "modify_membership")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def get_pending_requests (url, root_bundle, cert, key, cred_strings, member_uid, project_uid):
  req_data = xmlrpclib.dumps((member_uid, REQCTX.PROJECT, project_uid, cred_strings, {}),
                             methodname="get_pending_requests_for_user")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def resolve_request (url, root_bundle, cert, key, cred_strings, request_id, resolution, desc):
  req_data = xmlrpclib.dumps((REQCTX.PROJECT, request_id, resolution, desc, cred_strings, {}),
                             methodname="resolve_pending_request")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def create_request (url, root_bundle, cert, key, cred_strings, project_id, desc):
  JOIN = 0
  DUMMY_ATTRS = ""
  req_data = xmlrpclib.dumps((REQCTX.PROJECT, project_id, JOIN, desc, DUMMY_ATTRS, cred_strings, {}),
                             methodname="create_request")
  return _rpcpost(url, req_data, (cert,key), root_bundle)
