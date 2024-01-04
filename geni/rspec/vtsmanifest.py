# Copyright (c) 2014-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os

from lxml import etree as ET
import six

import geni.namespaces as GNS
from .pgmanifest import ManifestSvcLogin, ManifestSvcUser

XPNS = {'g' : GNS.REQUEST.name,
        'u' : GNS.USER.name,
        'v' : "http://geni.bssoftworks.com/rspec/ext/vts/manifest/1",
        's' : "http://geni.bssoftworks.com/rspec/ext/sdn/manifest/1"}

class UnhandledPortTypeError(Exception):
  def __init__ (self, typ):
    super(UnhandledPortTypeError, self).__init__()
    self.typ = typ
  def __str__ (self):
    return "Port type '%s' isn't supported by port builder.  Perhaps you should contribute some code?" % (self.typ)


class GenericPort(object):
  def __init__ (self, typ):
    self.client_id = None
    self.type = typ
    self.cross_sliver = False
    self._name = None
    self._dpname = None

  @classmethod
  def _fromdom (cls, elem):
    p = GenericPort(elem.get("type"))
    p.client_id = elem.get("client_id")
    return p

  def _decomposeClientID (self):
    # Assumes that the client_id is in the format "dp_name:port_name"
    if self.client_id.count(":") == 1:
      (self._dpname, self._name) = self.client_id.split(":")
    # Assumes that the client_id is in the format "dp_name:_x_:port_name"
    elif self.client_id.count(":") == 2: 
      (self._dpname, _, self._name) = self.client_id.split(":")
      self.cross_sliver = True

  @property
  def name (self):
    if not self._name:
      self._decomposeClientID()
    return self._name

  @property
  def dpname (self):
    if not self._dpname:
      self._decomposeClientID()
    return self._dpname


class InternalContainerPort(GenericPort):
  class NoMACAddressError(Exception):
    def __init__ (self, cid):
      super(InternalContainerPort.NoMACAddressError, self).__init__()
      self._cid = cid
    def __str__ (self):
      return "Port with client_id %s does not have MAC address." % (self._cid)

  def __init__ (self):
    super(InternalContainerPort, self).__init__("internal")
    self.remote_client_id = None
    self._macaddress = None
    self._alias = None
    self._remote_dpname = None

  @property
  def macaddress (self):
    if not self._macaddress:
      raise InternalContainerPort.NoMACAddressError(self.client_id)
    else:
      return self._macaddress

  @macaddress.setter
  def macaddress (self, val):
    self._macaddress = val

  @property
  def name (self):
    return self._alias

  @classmethod
  def _fromdom (cls, elem):
    p = InternalContainerPort()
    p.client_id = elem.get("client_id")
    p.remote_client_id = elem.get("remote-clientid")
    p.macaddress = elem.get("mac-address")
    p._alias = elem.get("name")

    return p

  @property
  def remote_dpname (self):
    if not self._remote_dpname:
      if self.remote_client_id.count(":") == 1:
        self._remote_dpname = self.remote_client_id.split(":")[0]
      elif self.remote_client_id.count(":") == 2:
        self._remote_dpname = self.remote_client_id.split(":")[0]
    return self._remote_dpname


class InternalPort(GenericPort):
  def __init__ (self):
    super(InternalPort, self).__init__("internal")
    self.remote_client_id = None
    self._remote_dpname = None
    self._vlan_id = None

  @classmethod
  def _fromdom (cls, elem):
    p = InternalPort()
    p.client_id = elem.get("client_id")
    p.remote_client_id = elem.get("remote-clientid")
    p.vlan_id = int(elem.get("vlan-id", 0))

    return p

  @property
  def remote_dpname (self):
    if not self._remote_dpname:
      if self.remote_client_id.count(":") == 1:
        self._remote_dpname = self.remote_client_id.split(":")[0]
      elif self.remote_client_id.count(":") == 2:
        self._remote_dpname = self.remote_client_id.split(":")[0]
    return self._remote_dpname


class GREPort(GenericPort):
  def __init__ (self):
    super(GREPort, self).__init__("gre")
    self.circuit_plane = None
    self.local_endpoint = None
    self.remote_endpoint = None

  @classmethod
  def _fromdom (cls, elem):
    p = GREPort()
    p.client_id = elem.get("client_id")
    endpe = elem.xpath("v:endpoint", namespaces=XPNS)[0]
    p.circuit_plane = endpe.get("circuit-plane")
    p.local_endpoint = endpe.get("local")
    p.remote_endpoint = endpe.get("remote")
    return p


class PGLocalPort(GenericPort):
  def __init__ (self):
    super(PGLocalPort, self).__init__("pg-local")
    self.shared_vlan = None

  @classmethod
  def _fromdom (cls, elem):
    p = PGLocalPort()
    p.client_id = elem.get("client_id")
    p.shared_vlan = elem.get("shared-lan")
    return p


class VFPort(GenericPort):
  def __init__ (self):
    super(VFPort, self).__init__("vf")
    self.remote_client_id = None

  @classmethod
  def _fromdom (cls, elem):
    p = cls()
    p.client_id = elem.get("client_id")
    p.remote_client_id = elem.get("remote-clientid")
    return p


class ManifestMount(object):
  def __init__ (self):
    self.type = None
    self.name = None
    self.path = None
    self.volid = None

  @classmethod
  def _fromdom (cls, elem):
    m = ManifestMount()
    m.type = elem.get("type")
    m.volid = elem.get("vol-id")
    m.name = elem.get("name")
    m.path = elem.get("path")
    return m


class ManifestContainer(object):
  def __init__ (self):
    self.client_id = None
    self.image = None
    self.sliver_id = None
    self.logins = []
    self.users = []
    self.ports = []
    self.mounts = []

  def __getitem__ (self, key):
    for port in self.ports:
      if port.name == key:
        return port

  @property
  def name (self):
    return self.client_id

  @classmethod
  def _fromdom (cls, elem):
    c = ManifestContainer()
    c.client_id = elem.get("client_id")
    c.image = elem.get("image")
    c.sliver_id = elem.get("sliver_id")

    logins = elem.xpath('g:services/g:login', namespaces = XPNS)
    for lelem in logins:
      l = ManifestSvcLogin._fromdom(lelem)
      c.logins.append(l)

    users = elem.xpath('g:services/u:services_user', namespaces = XPNS)
    for uelem in users:
      u = ManifestSvcUser._fromdom(uelem)
      c.users.append(u)

    ports = elem.xpath('v:port', namespaces = XPNS)
    for cport in ports:
      p = Manifest._buildPort(cport, True)
      c.ports.append(p)

    mounts = elem.xpath('v:mount', namespaces = XPNS)
    for melem in mounts:
      m = ManifestMount._fromdom(melem)
      c.mounts.append(m)

    return c

class ManifestFunction(object):
  def __init__ (self, client_id):
    self.client_id = client_id

  @classmethod
  def _fromdom (cls, elem):
    typ = elem.get("type")
    if typ == "sslvpn":
      f = SSLVPNFunction._fromdom(elem)
      return f


class ManifestDatapath(object):
  def __init__ (self):
    self.client_id = None
    self.image = None
    self.sliver_id = None
    self.ports = []
    self.mirror = None

  def __getitem__ (self, key):
    for port in self.ports:
      if port.name == key:
        return port

  @classmethod
  def _fromdom (cls, elem):
    # TODO: Add ports later
    dp = ManifestDatapath()
    dp.client_id = elem.get("client_id")
    dp.image = elem.get("image")
    dp.sliver_id = elem.get("sliver_id")

    mirror = elem.xpath('v:mirror', namespaces = XPNS)
    if mirror:
      dp.mirror = mirror[0].get("target")

    stp = elem.xpath('v:stp', namespaces = XPNS)
    if stp:
      dp.stp_mode = stp[0].get("type")

    ports = elem.xpath('v:port', namespaces = XPNS)
    for port in ports:
      p = Manifest._buildPort(port)
      dp.ports.append(p)
    return dp


class SSLVPNFunction(ManifestFunction):
  def __init__ (self, client_id):
    super(SSLVPNFunction, self).__init__(client_id)
    self.tp_port = None
    self.local_ip = None
    self.key = None
    self.note = None

  @classmethod
  def _fromdom (cls,elem):
    vpn = SSLVPNFunction(elem.get('client_id'))
    vpn.tp_port = elem.get('tp-port')
    vpn.local_ip = elem.get('local-ip')
    vpn.key = elem.text
    vpn.note = elem.get('note')
    return vpn

class Manifest(object):
  """Wrapper object for GENI XML manifest rspec, providing a pythonic API to the contained data"""

  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path, "rb"))
      self._xml = ET.tostring(self._root)
    elif xml:
      if six.PY3:
        self._xml = bytes(xml, "utf-8")
      else:
        self._xml = xml
      self._root = ET.fromstring(self._xml)
    self._pid = os.getpid()
    self._info = {}

  def _populate_info (self):
    ielems = self._root.xpath('v:info', namespaces = XPNS)
    if ielems:
      self._info["host"] = ielems[0].get("host")
      self._info["slice"] = ielems[0].get("slice")
      self._info["client-topo-name"] = ielems[0].get("client-topo-name")

  def __getitem__ (self, key):
    return self.findTarget(key)

  @property
  def root (self):
    if os.getpid() != self._pid:
      self._root = ET.fromstring(self._xml)
      self._pid = os.getpid()
    return self._root

  @property
  def text (self):
    """String representation of original XML content, with added whitespace for easier reading"""
    return ET.tostring(self._root, pretty_print=True, encoding="unicode")

  @property
  def pg_circuits (self):
    """Iterator for allocated circuit names on the local PG circuit plane (as strings)."""
    elems = self._root.xpath("v:datapath/v:port[@shared-lan]", namespaces = XPNS)
    for elem in elems:
      yield elem.get("shared-lan")

  local_circuits = pg_circuits

  @property
  def ports (self):
    """Iterator for all datapath and container ports as subclasses of :py:class:`GenericPort` objects."""
    for dp in self.datapaths:
      for p in dp.ports:
        yield p
    for c in self.containers:
      for p in c.ports:
        yield p

  @property
  def containers (self):
    """Iterator over all allocated containers as :py:class:`ManifestContainer` objects."""
    elems = self._root.xpath("v:container", namespaces = XPNS)
    for elem in elems:
      yield ManifestContainer._fromdom(elem)

  @property
  def functions (self):
    """Iterator over all allocated functions as :py:class:`ManifestFunction` objects."""
    elems = self._root.xpath("v:functions/v:function", namespaces = XPNS)
    for elem in elems:
      yield ManifestFunction._fromdom(elem)

  @property
  def datapaths (self):
    """Iterator over all allocated datapaths as :py:class:`ManifestDatapath` objects."""
    elems = self._root.xpath("v:datapath", namespaces = XPNS)
    for elem in elems:
      yield ManifestDatapath._fromdom(elem)

  @property
  def host (self):
    if not self._info:
      self._populate_info()
    return self._info["host"]

  @property
  def slicename (self):
    if not self._info:
      self._populate_info()
    return self._info["slice"]

  @property
  def toponame (self):
    if not self._info:
      self._populate_info()
    return self._info["client-topo-name"]

  def findTarget (self, client_id):
    """Get the container or datapath representing the given `client_id` in the manifest.

    Args:
      client_id (str): Requested client ID of the object you want to find

    Returns:
      :py:class:`ManifestDatapath`, :py:class:`ManifestContainer`, or `None`
    """
      
    dpelems = self._root.xpath("v:datapath[@client_id='%s']" % (client_id), namespaces = XPNS)
    if dpelems:
      return ManifestDatapath._fromdom(dpelems[0])

    ctelems = self._root.xpath("v:container[@client_id='%s']" % (client_id), namespaces = XPNS)
    if ctelems:
      return ManifestContainer._fromdom(ctelems[0])

  def findPort (self, client_id):
    """Get the datapath port object representing the given `client_id`.

    Args:
      client_id (str): client_id of the port you want to find

    Returns:
      :py:class:`GenericPort` or `None`
    """
    pelems = self._root.xpath("v:datapath/v:port[@client_id='%s']" % (client_id), namespaces = XPNS)
    if pelems:
      return Manifest._buildPort(pelems[0])

  @staticmethod
  def _buildPort (elem, container = False):
    t = elem.get("type")
    if t == "gre":
      return GREPort._fromdom(elem)
    elif t == "pg-local":
      return PGLocalPort._fromdom(elem)
    elif t == "vf-port":
      return VFPort._fromdom(elem)
    elif t == "internal":
      if container:
        return InternalContainerPort._fromdom(elem)
      else:
        return InternalPort._fromdom(elem)
    raise UnhandledPortTypeError(t)

  def write (self, path):
    """
.. deprecated:: 0.4
    Use :py:meth:`geni.rspec.vtsmanifest.Manifest.writeXML` instead."""

    import geni.warnings as GW
    import warnings
    warnings.warn("The Manifest.write() method is deprecated, please use Manifest.writeXML() instead",
                  GW.GENILibDeprecationWarning, 2)
    self.writeXML(path)

  def writeXML (self, path):
    """Write the XML representation of this manifest to the supplied path.

    Args:
      path (str): Path to output file
    """
    f = open(path, "w+")
    f.write(ET.tostring(self.root, pretty_print=True))
    f.close()

