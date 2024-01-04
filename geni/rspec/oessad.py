# Copyright (c) 2015-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from lxml import etree as ET
import six

from .. import namespaces as GNS
from .pg import Namespaces as PGNS
from . import stitching

_XPNS = {'g' : GNS.REQUEST.name, 'e' : PGNS.EMULAB.name, 't' : stitching.STITCHNS.name}

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
  def stitchinfo (self):
    """Reference to the stitching info in the manifest, if present."""
    try:
      elem = self._root.xpath('/g:rspec/t:stitching', namespaces=_XPNS)[0]
      return stitching.AdInfo(elem)
    except IndexError:
      return None

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True, encoding="unicode")
