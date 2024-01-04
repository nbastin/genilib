# Copyright (c) 2014-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from lxml import etree as ET
import six

import geni.namespaces as GNS
from geni.model.util import XPathXRange


VTSNS = GNS.Namespace("vts", "http://geni.bssoftworks.com/rspec/ext/vts/ad/1")
_XPNS = {'g' : GNS.REQUEST.name, 'v' : VTSNS.name}

def dumbcoerce (val):
  try:
    return int(val)
  except Exception:
    pass

  if val.lower() == "true": return True
  if val.lower() == "false": return False

  return val


class CircuitPlane(object):
  def __init__ (self):
    self.label = None
    self.type = None
    self.endpoint = None
    self.tunnel_types = []
    self.constraints = {}

  @classmethod
  def _fromdom (cls, elem):
    cp = CircuitPlane()
    cp.label = elem.get("label")
    supported = elem.xpath('v:supported-tunnels/v:tunnel-type', namespaces = _XPNS)

    for tuntyp in supported:
      cp.tunnel_types.append(tuntyp.get("name"))

    try:
      cp.endpoint = elem.xpath('v:endpoint', namespaces = _XPNS)[0].get("value")
    except IndexError:
      cp.endpoint = None

    for celem in elem.xpath('v:constraints/v:constraint', namespaces = _XPNS):
      cp.constraints[celem.get("key")] = dumbcoerce(celem.get("value"))

    return cp


class Image(object):
  def __init__ (self):
    self.name = None
    self.type = None
    self.mem_default = None
    self.mem_min = None
    self.mem_max = None

  def __str__ (self):
    return "[%s: %s]" % (self.type, self.name)

  @classmethod
  def _fromdom (cls, elem):
    img = cls()
    img.name = elem.get("name")
    img.type = elem.get("type")
    img.mem_default = int(elem.get("mem", 0))
    img.mem_min = int(elem.get("mem-min", img.mem_default))
    img.mem_max = int(elem.get("mem-max", img.mem_default))
    return img


class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path, "rb"))
    elif xml:
      if six.PY3:
        self._root = ET.fromstring(bytes(xml, "utf-8"))
      else:
        self._root = ET.fromstring(xml)

  @property
  def circuit_planes (self):
    return XPathXRange(self._root.xpath("v:circuit-planes/v:circuit-plane", namespaces = _XPNS), CircuitPlane)

  @property
  def images (self):
    return XPathXRange(self._root.xpath("v:images/v:image", namespaces = _XPNS), Image)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True, encoding="unicode")
