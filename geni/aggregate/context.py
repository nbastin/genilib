# Copyright (c) 2014-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import datetime
from io import open
import os
import os.path

import lxml.etree as ET

class SlicecredProxy(object):
  def __init__ (self, context):
    self._context = context

  def __getitem__ (self, name):
    return self._context._getSliceCred(name)

  def iteritems (self):
    return iter(self._context._slicecred_paths.items())

  def iterkeys (self):
    return iter(self._context._slicecred_paths.keys())

  def __iter__ (self):
    for x in self._context._slicecred_paths:
      yield x

class SliceCredInfo(object):
  class CredentialExpiredError(Exception):
    def __init__ (self, name, expires):
      super(SliceCredInfo.CredentialExpiredError, self).__init__()
      self.expires = expires
      self.sname = name
    def __str__ (self):
      return "Credential for slice %s expired on %s" % (self.sname, self.expires)

  def __init__ (self, context, slicename):
    self.slicename = slicename
    self.context = context
    self._path = None
    self.expires = None
    self.urn = None
    self.type = None
    self.version = None
    self._build()

  def _build (self):
    self._path = "%s/%s-%s-%s-scred.xml" % (self.context.datadir, self.context.cf.name,
                                            self.context.project, self.slicename)
    if not os.path.exists(self._path):
      self._downloadCredential()
    else:
      self._parseInfo()

  def _downloadCredential (self):
    cred = self.context.cf.getSliceCredentials(self.context, self.slicename)

    f = open(self._path, "wb+")
    f.write(cred)
    f.close()
    self._parseInfo()

  def _parseInfo (self):
    r = ET.parse(self._path)

    # Expiration
    expstr = r.find("credential/expires").text
    if expstr[-1] == 'Z':
      expstr = expstr[:-1]
    self.expires = datetime.datetime.strptime(expstr, "%Y-%m-%dT%H:%M:%S")

    # URN
    self.urn = r.find("credential/target_urn").text

    # Type
    tstr = r.find("credential/type").text.strip()
    if tstr == "privilege":
      self.type = "geni_sfa"
      self.version = 3  # We hope
    elif tstr == "abac":
      self.type = "abac"
      self.version = 1

  @property
  def path (self):
    checktime = datetime.datetime.now() + datetime.timedelta(days=3)
    if self.expires < checktime:
      # We expire in the next 6 days
      # TODO: Log something
      self._downloadCredential()
      if self.expires < datetime.datetime.now():
        raise SliceCredInfo.CredentialExpiredError(self.slicename, self.expires)
    return self._path

  @property
  def cred_api3 (self):
    scd = {"geni_type" : "geni_sfa", "geni_version" : 3}
    scd["geni_value"] = open(self.path, "r", encoding="latin-1").read()
    return scd


class Context(object):
  DEFAULT_DIR = os.path.expanduser("~/.bssw/geni")

  class UserCredExpiredError(Exception):
    def __init__ (self, expires):
      super(Context.UserCredExpiredError, self).__init__()
      self.expires = expires
    def __str__ (self):
      return "User Credential expired on %s" % (self.expires)

  def __init__ (self):
    self._data_dir = None
    self._nick_cache_path = None
    self._users = set()
    self._cf = None
    self._usercred_info = None  # (path, expires, urn, type, version)
    self._slicecreds = {}
    self.debug = False
    self.uname = None
    self.path = None

#  def save (self):
#    import geni._coreutil as GCU

#    obj = {}
#    obj["framework"] = context.cf.name
#    obj["cert-path"] = context.cf.cert_path
#    obj["key-path"] = context._key

  @property
  def userurn (self):
    return self._cf.userurn

  def _getSliceCred (self, sname):
    info = self.getSliceInfo(sname)
    return info.path

  def _getCredInfo (self, path):
    r = ET.parse(path)
    expstr = r.find("credential/expires").text
    if expstr[-1] == 'Z':
      expstr = expstr[:-1]
    exp = datetime.datetime.strptime(expstr, "%Y-%m-%dT%H:%M:%S")
    urn = r.find("credential/owner_urn").text

    # Type
    tstr = r.find("credential/type").text.strip()
    if tstr == "privilege":
      typ = "geni_sfa"
      version = 3  # We hope
    elif tstr == "abac":
      typ = "abac"
      version = 1

    return (exp, urn, typ, version)

  @property
  def _chargs (self):
    ucinfo = self._ucred_info
    ucd = {"geni_type" : ucinfo[3], "geni_version" : ucinfo[4]}
    ucd["geni_value"] = open(ucinfo[0], "r", encoding="latin-1").read()
    return (False, self.cf.cert, self.cf.key, [ucd])

  @property
  def ucred_api3 (self):
    ucinfo = self._ucred_info
    ucd = {"geni_type" : ucinfo[3], "geni_version" : ucinfo[4]}
    ucd["geni_value"] = open(ucinfo[0], "r", encoding="latin-1").read()
    return ucd

  @property
  def ucred_pg (self):
    return open(self._ucred_info[0], "r", encoding="latin-1").read()

  @property
  def project (self):
    return self.cf.project

  @project.setter
  def project (self, val):
    self.cf.project = val

  @property
  def project_urn (self):
    return self.cf.projecturn

  @property
  def cf (self):
    return self._cf

  @cf.setter
  def cf (self, value):
    # TODO: Calllback into framework here?  Maybe addressed with ISSUE-2
    # Maybe declare writing the _cf more than once as Unreasonable(tm)?
    self._cf = value
    self._usercred_info = None

  @property
  def nickCache (self):
    if self._nick_cache_path is None:
      cachepath = os.path.normpath("%s/nickcache.json" % (self.datadir))
      self._nick_cache_path = cachepath
    return self._nick_cache_path

  @property
  def datadir (self):
    if self._data_dir is None:
      if not os.path.exists(Context.DEFAULT_DIR):
        os.makedirs(Context.DEFAULT_DIR)
      self._data_dir = Context.DEFAULT_DIR
    return self._data_dir

  @datadir.setter
  def datadir (self, val):
    nval = os.path.expanduser(os.path.normpath(val))
    if not os.path.exists(nval):
      os.makedirs(nval)
    self._data_dir = nval

### TODO: User credentials need to belong to Users, or fix up this profile nonsense
  @property
  def _ucred_info (self):
    if (self._usercred_info is None) or (self._usercred_info[1] < datetime.datetime.now()):
      ucpath = "%s/%s-%s-usercred.xml" % (self.datadir, self.cf.name, self.uname)
      if not os.path.exists(ucpath):
        cred = self.cf.getUserCredentials(self.userurn)

        f = open(ucpath, "wb+")
        f.write(cred)
        f.close()

      (expires, urn, typ, version) = self._getCredInfo(ucpath)
      self._usercred_info = (ucpath, expires, urn, typ, version)

    if self._usercred_info[1] < datetime.datetime.now():
      cred = self.cf.getUserCredentials(self.userurn)
      f = open(ucpath, "wb+")
      f.write(cred)
      f.close()
      (expires, urn, typ, version) = self._getCredInfo(ucpath)
      self._usercred_info = (ucpath, expires, urn, typ, version)

    return self._usercred_info

  @property
  def usercred_path (self):
    # If you only need a user cred, something that works in the next 5 minutes is fine.  If you
    # are doing something more long term then you need a slice credential anyhow, whose
    # expiration will stop you as it should not outlast the user credential (and if it does,
    # some clearinghouse has decided that is allowed).
    checktime = datetime.datetime.now() + datetime.timedelta(minutes=5)
    if self._ucred_info[1] < checktime:
      # Delete the user cred and hope you already renewed it
      try:
        os.remove(self._ucred_info[0])
        self._usercred_info = None
      except OSError:
        # Windows won't let us remove open files
        # TODO: A place for some debug logging
        pass

    if self._ucred_info[1] < datetime.datetime.now():
      raise Context.UserCredExpiredError(self._ucred_info[1])

    return self._ucred_info[0]

  def addUser (self, user):
    self._users.add(user)
    # The first time we call this, it's from context loading, we hope
    # So, the first user is us, and not wacky other people
    # TODO: This is still stupid, and we need to separate framework accounts from resource accounts
    if not self.uname:
      self.uname = user.name

  @property
  def slicecreds (self):
    return SlicecredProxy(self)

  def getSliceInfo (self, sname, project = None):
    if not project:
      project = self.project
    if not ("%s-%s" % (project, sname) in self._slicecreds):
      scinfo = SliceCredInfo(self, sname)
      self._slicecreds["%s-%s" % (project, sname)] = scinfo
    return self._slicecreds["%s-%s" % (project, sname)]
