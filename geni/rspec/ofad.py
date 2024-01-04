# Copyright (c) 2014-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from lxml import etree as ET
import six

import geni.namespaces as GNS
from .pgad import Location

TOPO = GNS.Namespace("topo", "http://geni.bssoftworks.com/rspec/ext/topo/1")

XPNS = {'g' : GNS.REQUEST.name, 'o' : GNS.OFv3.name, 't' : TOPO.name}

class Attachment(object):
  def __init__ (self):
    self.description = None

class OFAttachment(Attachment):
  def __init__ (self):
    super(OFAttachment, self).__init__()
    self.remote_cmid = None
    self.remote_port_name = None

  @classmethod
  def _fromdom (cls, elem):
    a = OFAttachment()
    a.description = elem.get("desc")
    a.remote_cmid = elem.get("remote-component-id")
    a.remote_port_name = elem.get("remote-port-name")
    return a


class Port(object):
  def __init__ (self):
    self.name = None
    self.number = None
    self.topo = []

  def __repr__ (self):
    return "<Port %s,%s>" % (self.name, self.number)

  @classmethod
  def _fromdom (cls, elem):
    p = Port()
    p.name = elem.get("name")
    p.number = elem.get("number")
    for ofa in elem.xpath('t:geni-of', namespaces = XPNS):
      p.topo.append(OFAttachment._fromdom(ofa))
    return p


class Datapath(object):
  def __init__ (self):
    self.dpid = None
    self.component_id = None
    self.ports = []
    self.location = None

  @classmethod
  def _fromdom (cls, elem):
    d = Datapath()
    d.dpid = elem.get("dpid")
    d.component_id = elem.get("component_id")

    ports = elem.xpath('o:port', namespaces = XPNS)
    for pelem in ports:
      d.ports.append(Port._fromdom(pelem))

    lelem = elem.xpath('o:location', namespaces = XPNS)
    if lelem:
      d.location = Location._fromdom(lelem[0])

    return d


class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      if six.PY3:
        self._root = ET.fromstring(bytes(xml, "utf-8"))
      else:
        self._root = ET.fromstring(xml)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True, encoding="unicode")

  @property
  def datapaths (self):
    for datapath in self._root.findall("{%s}datapath" % (GNS.OFv3.name)):
      yield Datapath._fromdom(datapath)
