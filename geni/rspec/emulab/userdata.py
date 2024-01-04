# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from lxml import etree as ET

from ..pg import Node, Link, Request, Namespaces

class UserDataSet(object):
  def __init__ (self, data=None, prefix="emulab.net.userdata."):
    if data is not None:
      self.data = data
    else:
      self.data = {}
    self.prefix = prefix

  def addData (self, element, data=None):
    if isinstance(element, dict):
      self.data.update(element)
    elif data is not None:
      self.data[element] = data


class UserData(object):
  def __init__ (self, userdata):
    self.userdata = None
    if isinstance(userdata, UserDataSet):
      self.userdata = userdata

  def _write (self, element):
    if self.userdata is not None:
      ud = ET.SubElement(element, "data_set",
                         nsmap={None : Namespaces.PARAMS.name})
      for key, value in self.userdata.data.iteritems():
        udi = ET.SubElement(ud, "data_item")
        udi.attrib["name"] = self.userdata.prefix + key

        if isinstance(value, ET._Element):
          udi.append(value)
        else:
          udi.text = value
      return ud

Node.EXTENSIONS.append(("UserData", UserData))
Link.EXTENSIONS.append(("UserData", UserData))
