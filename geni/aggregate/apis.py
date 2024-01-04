# Copyright (c) 2014-2018  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, unicode_literals

from io import open

from .core import APIRegistry
from .exceptions import AMError
from . import pgutil as ProtoGENI

# pylint: disable=multiple-statements
class AllocateError(AMError): pass
class CreateSliverError(AMError): pass
class DeleteSliverError(AMError): pass
class GetVersionError(AMError): pass
class ListResourcesError(AMError): pass
class ProvisionError(AMError): pass
class RenewSliverError(AMError): pass
class SliverStatusError(AMError): pass
class POAError(AMError): pass
# pylint: enable=multiple-statements


class AMAPIv3(object):
  @staticmethod
  def poa (context, url, sname, action, urns = None, options = None):
    from ..minigcf import amapi3 as AM3

    sinfo = context.getSliceInfo(sname)
    if not urns:
      urns = [sinfo.urn]

    res = AM3.poa(url, False, context.cf.cert, context.cf.key, [sinfo], urns, action, options)
    if res["code"]["geni_code"] == 0:
      return res["value"]

    if "am_type" in res["code"]:
      if res["code"]["am_type"] == "protogeni":
        ProtoGENI.raiseError(res)

    raise POAError(res["output"], res)

  @staticmethod
  def paa (context, url, action, options = None):
    from ..minigcf import amapi3 as AM3

    res = AM3.paa(url, False, context.cf.cert, context.cf.key, action, options)
    if res["code"]["geni_code"] == 0:
      return res["value"]

    raise POAError(res["output"], res)

  @staticmethod
  def allocate (context, url, sname, rspec, options = None):
    if not options: options = {}
    from ..minigcf import amapi3 as AM3

    sinfo = context.getSliceInfo(sname)

    res = AM3.allocate(url, False, context.cf.cert, context.cf.key, [sinfo], sinfo.urn, rspec, options)
    if res["code"]["geni_code"] == 0:
      return res
    if "am_type" in res["code"]:
      if res["code"]["am_type"] == "protogeni":
        ProtoGENI.raiseError(res)
    raise AllocateError(res["output"], res)

  @staticmethod
  def provision (context, url, sname, urns = None, options = None):
    from ..minigcf import amapi3 as AM3

    if not options: options = {}
    if urns is not None:
      if not isinstance(urns, list): urns = [urns]

    sinfo = context.getSliceInfo(sname)
    if not urns:
      urns = [sinfo.urn]

    res = AM3.provision(url, False, context.cf.cert, context.cf.key, [sinfo], urns, options)
    if res["code"]["geni_code"] == 0:
      return res
    if "am_type" in res["code"]:
      if res["code"]["am_type"] == "protogeni":
        ProtoGENI.raiseError(res)
    raise ProvisionError(res["output"], res)

  @staticmethod
  def delete (context, url, sname, urns, options = None):
    from ..minigcf import amapi3 as AM3

    if not options: options = {}
    if not isinstance(urns, list): urns = [urns]

    sinfo = context.getSliceInfo(sname)

    res = AM3.delete(url, False, context.cf.cert, context.cf.key, [sinfo], urns, options)
    if res["code"]["geni_code"] == 0:
      return res
    if res["code"].has_key("am_type"):
      if res["code"]["am_type"] == "protogeni":
        ProtoGENI.raiseError(res)
    raise ProvisionError(res["output"], res)


class AMAPIv2(object):
  @staticmethod
  def listresources (context, url, sname, options = None):
    if not options: options = {}

    from ..minigcf import amapi2 as AM2
    creds = []

    surn = None
    if sname:
      sinfo = context.getSliceInfo(sname)
      surn = sinfo.urn
      creds.append(open(sinfo.path, "r", encoding="latin-1").read())

    creds.append(open(context.usercred_path, "r", encoding="latin-1").read())

    res = AM2.listresources(url, False, context.cf.cert, context.cf.key, creds, options, surn)
    if res["code"]["geni_code"] == 0:
      return res
    if "am_type" in res["code"]:
      if res["code"]["am_type"] == "protogeni":
        ProtoGENI.raiseError(res)

    raise ListResourcesError(res["output"], res)

  @staticmethod
  def createsliver (context, url, sname, rspec):
    from ..minigcf import amapi2 as AM2

    sinfo = context.getSliceInfo(sname)
    cred_data = open(sinfo.path, "r", encoding="latin-1").read()

    udata = []
    for user in context._users:
      data = {"urn" : user.urn, "keys" : [open(x, "r", encoding="latin-1").read() for x in user._keys]}
      udata.append(data)

    res = AM2.createsliver(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn, rspec, udata)
    if res["code"]["geni_code"] == 0:
      return res
    if "am_type" in res["code"]:
      if res["code"]["am_type"] == "protogeni":
        ProtoGENI.raiseError(res)
    raise CreateSliverError(res["output"], res)

  @staticmethod
  def sliverstatus (context, url, sname):
    from ..minigcf import amapi2 as AM2

    sinfo = context.getSliceInfo(sname)
    cred_data = open(sinfo.path, "r", encoding="latin-1").read()

    res = AM2.sliverstatus(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn)
    if res["code"]["geni_code"] == 0:
      return res["value"]
    if "am_type" in res["code"]:
      if res["code"]["am_type"] == "protogeni":
        ProtoGENI.raiseError(res)
    raise SliverStatusError(res["output"], res)

  @staticmethod
  def renewsliver (context, url, sname, date):
    from ..minigcf import amapi2 as AM2

    sinfo = context.getSliceInfo(sname)
    cred_data = open(sinfo.path, "r", encoding="latin-1").read()

    res = AM2.renewsliver(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn, date)
    if res["code"]["geni_code"] == 0:
      return res["value"]
    raise RenewSliverError(res["output"], res)

  @staticmethod
  def deletesliver (context, url, sname):
    from ..minigcf import amapi2 as AM2

    sinfo = context.getSliceInfo(sname)
    cred_data = open(sinfo.path, "r", encoding="latin-1").read()

    res = AM2.deletesliver(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn)
    if res["code"]["geni_code"] == 0:
      return res["value"]
    raise DeleteSliverError(res["output"], res)

  @staticmethod
  def getversion (context, url):
    from ..minigcf import amapi2 as AM2

    res = AM2.getversion(url, False, context.cf.cert, context.cf.key)
    if res["code"]["geni_code"] == 0:
      return res["value"]
    raise GetVersionError(res["output"], res)


APIRegistry.register("amapiv2", AMAPIv2())
APIRegistry.register("amapiv3", AMAPIv3())

