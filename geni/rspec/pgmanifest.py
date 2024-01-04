# Copyright (c) 2013-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os

from lxml import etree as ET
import six

from .pg import Link
from .. import namespaces as GNS
from .pg import Namespaces as PGNS
from ..model.util import XPathXRange

_XPNS = {'g' : GNS.REQUEST.name, 's' : GNS.SVLAN.name, 'e' : PGNS.EMULAB.name,
         'i' : PGNS.INFO.name, 'p' : PGNS.PARAMS.name, 'u' : GNS.USER.name}

class ManifestLink(Link):
  def __init__ (self):
    super(ManifestLink, self).__init__()
    self.interface_refs = []
    self.sliver_id = None
    self.vlan = None
    self._elem = None

  @classmethod
  def _fromdom (cls, elem):
    lnk = ManifestLink()
    lnk._elem = elem
    lnk.client_id = elem.get("client_id")
    lnk.sliver_id = elem.get("sliver_id")
    lnk.vlan = elem.get("vlantag", None)

    refs = elem.xpath('g:interface_ref', namespaces = _XPNS)
    for ref in refs:
      lnk.interface_refs.append(ref.get("sliver_id"))

    svlans = elem.xpath('s:link_shared_vlan', namespaces = _XPNS)
    if svlans:
      # TODO: Can a link be attached to more than one shared vlan?
      # Don't believe PG supports trunks, but the rspec doesn't really forbid it
      lnk.vlan = svlans[0].get("name")

    return lnk

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True, encoding="unicode")


class ManifestSvcLogin(object):
  def __init__ (self):
    self.auth = None
    self.hostname = None
    self.port = None
    self.username = None

  @classmethod
  def _fromdom (cls, elem):
    n = ManifestSvcLogin()
    n.auth = elem.get("authentication")
    n.hostname = elem.get("hostname")
    n.port = int(elem.get("port"))
    n.username = elem.get("username")

    return n


class ManifestSvcUser(object):
  def __init__ (self):
    self.login = None
    self.public_key = None

  @classmethod
  def _fromdom (cls, elem):
    n = cls()
    n.login = elem.get("login")
    pkelems = elem.xpath('u:public_key', namespaces = _XPNS)
    if pkelems:
      n.public_key = pkelems[0].text.strip()
    return n


class ManifestNode(object):
  class Interface(object):
    def __init__ (self):
      self.client_id = None
      self.mac_address = None
      self.sliver_id = None
      self.address_info = None
      self.component_id = None

  def __init__ (self):
    super(ManifestNode, self).__init__()
    self.logins = []
    self.users = []
    self.interfaces = []
    self.client_id = None
    self.component_id = None
    self.sliver_id = None
    self._elem = None
    self._hostfqdn = None
    self._hostipv4 = None

  @property
  def name (self):
    return self.client_id

  @property
  def hostfqdn (self):
    if not self._hostfqdn:
      self._populateHostInfo()
    return self._hostfqdn

  @property
  def hostipv4 (self):
    if not self._hostipv4:
      self._populateHostInfo()
    return self._hostipv4

  def _populateHostInfo (self):
    host = self._elem.xpath('g:host', namespaces = _XPNS)
    if host:
      self._hostfqdn = host[0].get("name", None)
      self._hostipv4 = host[0].get("ipv4", None)

  @classmethod
  def _fromdom (cls, elem):
    n = ManifestNode()
    n._elem = elem
    n.client_id = elem.get("client_id")
    n.component_id = elem.get("component_id")
    n.sliver_id = elem.get("sliver_id")

    logins = elem.xpath('g:services/g:login', namespaces = _XPNS)
    for lelem in logins:
      l = ManifestSvcLogin._fromdom(lelem)
      n.logins.append(l)

    users = elem.xpath('g:services/u:services_user', namespaces = _XPNS)
    for uelem in users:
      u = ManifestSvcUser._fromdom(uelem)
      n.users.append(u)

    interfaces = elem.xpath('g:interface', namespaces = _XPNS)
    for ielem in interfaces:
      i = ManifestNode.Interface()
      i.client_id = ielem.get("client_id")
      i.sliver_id = ielem.get("sliver_id")
      i.component_id = ielem.get("component_id")
      i.mac_address = ielem.get("mac_address")
      try:
        ipelem = ielem.xpath('g:ip', namespaces = _XPNS)[0]
        i.address_info = (ipelem.get("address"), ipelem.get("netmask"))
      except Exception:
        pass
      n.interfaces.append(i)

    return n

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True, encoding="unicode")


class ManifestParameter(object):
  def __init__ (self, name, value):
    super(ManifestParameter, self).__init__()
    self.name = name
    self.value = value

  @classmethod
  def _fromdom (cls, elem):
    n = ManifestParameter(elem.get('name'), elem.get('value'))
    return n


class Manifest(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._xml = open(path, "r").read()
    elif xml:
      if six.PY3:
        self._xml = bytes(xml, "utf-8")
      else:
        self._xml = xml
    self._root = ET.fromstring(self._xml)
    self._pid = os.getpid()

  @property
  def root (self):
    if os.getpid() != self._pid:
      self._root = ET.fromstring(self._xml)
      self._pid = os.getpid()
    return self._root

  @property
  def latitude (self):
    loc = self._root.xpath('i:site_info/i:location', namespaces = _XPNS)
    if loc:
      return loc[0].get("latitude")

  @property
  def longitude (self):
    loc = self._root.xpath('i:site_info/i:location', namespaces = _XPNS)
    if loc:
      return loc[0].get("longitude")

  @property
  def expiresstr (self):
    return self._root.get("expires")

  @property
  def links (self):
    return XPathXRange(self.root.findall("{%s}link" % (GNS.REQUEST)), ManifestLink)

  @property
  def nodes (self):
    return XPathXRange(self.root.findall("{%s}node" % (GNS.REQUEST)), ManifestNode)

  @property
  def parameters (self):
    for param in self.root.findall("{%s}data_set/{%s}data_item"
                                   % (PGNS.PARAMS.name,PGNS.PARAMS.name)):
      yield ManifestParameter._fromdom(param)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True, encoding="unicode")

  def _repr_html_ (self):
    return """
<table>
  <tr><th scope="row">Expires</th><td>%s</td></tr>
  <tr><th scope="row">Nodes</th><td>%d</td></tr>
  <tr><th scope="row">Links</th><td>%d</td></tr>
  <tr><th scope="row">Location</th><td>%s, %s</td></tr>
</table>""" % (self.expiresstr, len(self.nodes), len(self.links),
               self.latitude, self.longitude)

  def write (self, path):
    """
.. deprecated:: 0.4
    Use :py:meth:`geni.rspec.pg.Request.writeXML` instead."""

    import geni.warnings as GW
    import warnings
    warnings.warn("The Manifest.write() method is deprecated, please use Manifest.writeXML() instead",
                  GW.GENILibDeprecationWarning, 2)
    self.writeXML(path)

  def writeXML (self, path):
    """Write the current manifest as an XML file that contains an rspec in the format returned by the
    aggregate."""
    f = open(path, "w+")
    f.write(ET.tostring(self.root, pretty_print=True))
    f.close()
