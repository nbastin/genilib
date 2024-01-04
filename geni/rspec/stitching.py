# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import datetime

from lxml import etree as ET

from . import pg
from .. import namespaces
from ..model.util import XPathXRange

STITCHNS = namespaces.Namespace("stitch", "http://hpn.east.isi.edu/rspec/ext/stitch/0.1/")

_XPNS = {'t' : STITCHNS.name}

class StitchInfo(pg.Resource):
  def __init__ (self):
    super(StitchInfo, self).__init__()
    self._paths = []
    self.addNamespace(STITCHNS)

  def addPath (self, path):
    self._paths.append(path)
    return path

  def _write (self, element):
    se = ET.SubElement(element, "{%s}stitching" % (STITCHNS))
    se.attrib["lastUpdateTime"] = datetime.datetime.now().strftime("%Y%m%d:%H:%M:%S")

    for path in self._paths:
      path._write(se)

    return se


class Path(object):
  def __init__ (self, name):
    self.name = name
    self._hops = []

  def addHop (self, hop):
    self._hops.append(hop)
    return hop

  def _write (self, element):
    pe = ET.SubElement(element, "{%s}path" % (STITCHNS))
    pe.attrib["id"] = self.name

    # We wait until writing to give them IDs, so you can do all kinds of stupid things
    # like reordering and deleting until then
    for idx,hop in enumerate(self._hops, start=1):
      hop._id = idx
      if len(self._hops) != idx:
        hop._next_hop_id = idx+1

    for hop in self._hops:
      hop._write(pe)

    return pe


class Hop(object):
  def __init__ (self):
    self.link_id = None
    self.capacity = 1
    self.suggested_vlan = None
    self._id = None
    self._next_hop_id = None

    # Don't override these unless the aggregate hates you
    self.ad_vrange_low = 1
    self.ad_vrange_high = 4092
    self.vlan_translation = False

  def _write (self, element):
    he = ET.SubElement(element, "{%s}hop" % (STITCHNS))
    he.attrib["id"] = "%d" % (self._id)

    link = ET.SubElement(he, "{%s}link" % (STITCHNS))
    link.attrib["id"] = self.link_id

    tem = ET.SubElement(link, "{%s}trafficEngineeringMetric" % (STITCHNS))
    tem.text = "10"

    ce = ET.SubElement(link, "{%s}capacity" % (STITCHNS))
    ce.text = "%d" % (self.capacity)

    scd = ET.SubElement(link, "{%s}switchingCapabilityDescriptor" % (STITCHNS))

    sct = ET.SubElement(scd, "{%s}switchingcapType" % (STITCHNS))
    sct.text = "l2sc"

    enc = ET.SubElement(scd, "{%s}encodingType" % (STITCHNS))
    enc.text = "ethernet"

    scs = ET.SubElement(scd, "{%s}switchingCapabilitySpecificInfo" % (STITCHNS))
    l2scs = ET.SubElement(scs, "{%s}switchingCapabilitySpecificInfo_L2sc" % (STITCHNS))

    imtu = ET.SubElement(l2scs, "{%s}interfaceMTU" % (STITCHNS))
    imtu.text = "1500"

    vra = ET.SubElement(l2scs, "{%s}vlanRangeAvailability" % (STITCHNS))
    vra.text = "%d-%d" % (self.ad_vrange_low, self.ad_vrange_high)

    svr = ET.SubElement(l2scs, "{%s}suggestedVLANRange" % (STITCHNS))
    svr.text = "%d" % (self.suggested_vlan)

    vt = ET.SubElement(l2scs, "{%s}vlanTranslation" % (STITCHNS))
    vt.text = str(self.vlan_translation).lower()

    nh = ET.SubElement(he, "{%s}nextHop" % (STITCHNS))
    if self._next_hop_id:
      nh.text = "%d" % (self._next_hop_id)
    else:
      nh.text = "null"

    return he

def coerceBool (text):
  if text.lower() == "false":
    return False
  elif text.lower() == "true":
    return True
  else:
    return None

class AdInfo(object):
  def __init__ (self, elem):
    self._root = elem
    self._aggregates = {}

  @property
  def aggregates (self):
    if not self._aggregates:
      for elem in self._root.xpath('t:aggregate', namespaces=_XPNS):
        info = AggInfo(elem)
        self._aggregates[info.urn] = info
    return self._aggregates


class AggInfo(object):
  def __init__ (self, elem):
    self._root = elem
    self.urn = elem.get("id")
    self.url = elem.get("url")

  @property
  def mode (self):
    return self._root.xpath("t:stitchingmode", namespaces=_XPNS)[0].text

  @property
  def scheduledservices (self):
    t = self._root.xpath("t:scheduledservices", namespaces=_XPNS)[0].text
    return coerceBool(t)

  @property
  def negotiatedservices (self):
    t = self._root.xpath("t:negotiatedservices", namespaces=_XPNS)[0].text
    return coerceBool(t)

  @property
  def nodes (self):
    n = self._root.xpath("t:node", namespaces=_XPNS)
    return XPathXRange(n, AggNode)


class AggNode(object):
  def __init__ (self):
    self.id = None
    self._root = None

  @property
  def ports (self):
    p = self._root.xpath("t:port", namespaces=_XPNS)
    return XPathXRange(p, AggPort)

  @classmethod
  def _fromdom (cls, elem):
    node = AggNode()
    node._root = elem
    node.id = elem.get("id")
    return node


class AggPort(object):
  def __init__ (self):
    self.id = None
    self.capacity = 0
    self._root = None

  @property
  def links (self):
    l = self._root.xpath("t:link", namespaces=_XPNS)
    return XPathXRange(l, AggLink)

  @classmethod
  def _fromdom (cls, elem):
    port = AggPort()
    port._root = elem
    port.id = elem.get("id")
    port.capacity = int((elem.xpath("t:capacity", namespaces=_XPNS)[0].text).strip("kbps"))
    return port


class AggLink(object):
  def __init__ (self):
    self._root = None
    self.id = None
    self.remote_urn = None

  @property
  def al2sinfo (self):
    if not self.remote_urn.count("al2s.internet2.edu"):
      return None
    parts = self.remote_urn.split(":")
    port = parts[-2]
    switch = parts[-3].split("+")[-1]
    return (switch, port)

  @classmethod
  def _fromdom (cls, elem):
    link = AggLink()
    link._root = elem
    link.id = elem.get("id")
    link.remote_urn = elem.xpath("t:remoteLinkId", namespaces=_XPNS)[0].text
    return link
