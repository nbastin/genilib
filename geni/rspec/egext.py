# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from __future__ import absolute_import

from lxml import etree as ET

from .. import namespaces as GNS
from .pg import Node

class DiskImage(object):
  def __init__ (self, name, version):
    self.name = name
    self.version = version

  def _write (self, element):
    di = ET.SubElement(element, "{%s}disk_image" % (GNS.REQUEST.name))
    di.attrib["name"] = self.name
    di.attrib["version"] = self.version
    return di

class XOSmall(Node):
  def __init__ (self, name, component_id = None):
    super(XOSmall, self).__init__(name, "xo.small", component_id, None)

class XOMedium(Node):
  def __init__ (self, name, component_id = None):
    super(XOMedium, self).__init__(name, "xo.medium", component_id, None)

class XOLarge(Node):
  def __init__ (self, name, component_id = None):
    super(XOLarge, self).__init__(name, "xo.large", component_id, None)
