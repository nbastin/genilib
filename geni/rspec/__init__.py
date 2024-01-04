# Copyright (c) 2013  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from lxml import etree as ET
import geni.namespaces as GNS

class RSpec (object):
  def __init__ (self, rtype):
    self.NSMAP = {}
    self._nsnames = set()
    self._loclist = []
    self.addNamespace(GNS.XSNS)
    self.type = rtype

  def addNamespace (self, ns, prefix = ""):
    if ns.name in self._nsnames:
      return

    self._nsnames.add(ns.name)

    if prefix != "":
      self.NSMAP[prefix] = ns.name
    else:
      self.NSMAP[ns.prefix] = ns.name

    if ns.location is not None:
      self._loclist.append(ns.name)
      self._loclist.append(ns.location)

  def toXMLString (self, pretty_print = False, ucode=False):
    rspec = self.getDOM()
    if ucode:
      return ET.tostring(rspec, pretty_print = pretty_print, encoding="unicode")
    else:
      return ET.tostring(rspec, pretty_print = pretty_print)

  def getDOM (self):
    rspec = ET.Element("rspec", nsmap = self.NSMAP)
    rspec.attrib["{%s}schemaLocation" % (GNS.XSNS.name)] = " ".join(self._loclist)
    rspec.attrib["type"] = self.type
    return rspec
