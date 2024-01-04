# Copyright (c) 2014-2017  Barnstormer Softworks, Ltd.
# Copyright (c) 2020  University of Houston Networking Lab

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import base64
import functools
import decimal

import ipaddress
from lxml import etree as ET
import six

import geni.rspec
import geni.namespaces as GNS
from geni.rspec.pg import Resource


class Namespaces(object):
  VTS = GNS.Namespace("vts", "http://geni.bssoftworks.com/rspec/ext/vts/request/1")
  SDN = GNS.Namespace("sdn", "http://geni.bssoftworks.com/rspec/ext/sdn/request/1")

class BadImageTypeError(Exception):
  def __init__ (self, rtype):
    self.rtype = rtype
  def __str__ (self):
    return "Supplied image must be of type %s" % (self.rtype)

################################################
# Base Request - Must be at top for EXTENSIONS #
################################################

class Request(geni.rspec.RSpec):
  EXTENSIONS = []

  def __init__ (self):
    super(Request, self).__init__("request")
    self._resources = []
    self.topo_name = None

    self.addNamespace(GNS.REQUEST, None)
    self.addNamespace(Namespaces.VTS)
    self.addNamespace(Namespaces.SDN)

    self._ext_children = []
    for name,ext in Request.EXTENSIONS:
      self._wrapext(name,ext)

  def _wrapext (self, name, klass):
    @functools.wraps(klass.__init__)
    def wrap(*args, **kw):
      instance = klass(*args, **kw)
      self._ext_children.append(instance)
      return instance
    setattr(self, name, wrap)

  def addResource (self, rsrc):
    for ns in rsrc.namespaces:
      self.addNamespace(ns)
    self._resources.append(rsrc)

  def writeXML (self, path):
    f = open(path, "w+")
    f.write(self.toXMLString(True))
    f.close()

  def toXMLString (self, pretty_print = False, ucode = False):
    rspec = self.getDOM()

    if self.topo_name:
      ci = ET.SubElement(rspec, "{%s}client-info" % (Namespaces.VTS))
      ci.attrib["topo-name"] = str(self.topo_name)

    for resource in self._resources:
      resource._write(rspec)

    for obj in self._ext_children:
      obj._write(rspec)

    if ucode:
      buf = ET.tostring(rspec, pretty_print = pretty_print, encoding="unicode")
    else:
      buf = ET.tostring(rspec, pretty_print = pretty_print)

    return buf

  @property
  def resources(self):
      return self._resources + self._ext_children

######################
# Internal Functions #
######################

def _am_encrypt (gv, plaintext):
  # This should be turned into an Encryptor object that you can init once and carry around
  from cryptography.hazmat.backends import default_backend
  from cryptography.hazmat.primitives import hashes, serialization
  from cryptography.hazmat.primitives.asymmetric import padding

  pubkey = serialization.load_pem_public_key(gv["request.pubkey"], backend=default_backend())

  if gv["request.hash"] == "sha1":
    hfunc = hashes.SHA1
  elif gv["request.hash"] == "sha256":
    hfunc = hashes.SHA256
  elif gv["request.hash"] == "sha384":
    hfunc = hashes.SHA384
  elif gv["request.hash"] == "sha512":
    hfunc = hashes.SHA512

  return base64.b64encode(pubkey.encrypt(plaintext, padding.OAEP(padding.MGF1(hfunc()), hfunc(), None)))


###################
# Utility Objects #
###################

class DelayInfo(object):
  def __init__ (self, time = None, jitter = None, correlation = None, distribution = None):
    self.time = time
    self.jitter = jitter
    self.correlation = correlation
    self.distribution = distribution

  def __json__ (self):
    d = {"type" : "egress-delay"}
    if self.time: d["time"] = self.time
    if self.jitter: d["jitter"] = self.jitter
    if self.correlation: d["correlation"] = self.correlation
    if self.distribution: d["distribution"] = self.distribution
    return d

  def _write (self, element):
    d = ET.SubElement(element, "{%s}egress-delay" % (Namespaces.VTS.name))
    if self.time: d.attrib["time"] = str(self.time)
    if self.jitter: d.attrib["jitter"] = str(self.jitter)
    if self.correlation: d.attrib["correlation"] = str(self.correlation)
    if self.distribution: d.attrib["distribution"] = self.distribution
    return d


class LossInfo(object):
  def __init__ (self, percent):
    self.percent = percent

  def __json__ (self):
    return {"type" : "egress-loss", "percent" : "%d" % (self.percent)}

  def _write (self, element):
    d = ET.SubElement(element, "{%s}egress-loss" % (Namespaces.VTS))
    d.attrib["percent"] = "%d" % (self.percent)
    return d


class ReorderInfo(object):
  def __init__ (self, percent, correlation, gap = None):
    self.percent = percent
    self.correlation = correlation
    self.gap = gap

  def _write (self, element):
    d = ET.SubElement(element, "{%s}egress-reorder" % (Namespaces.VTS))
    d.attrib["percent"] = str(self.percent)
    d.attrib["correlation"] = str(self.correlation)
    if self.gap:
      d.attrib["gap"] = str(self.gap)
    return d


###################
# Datapath Images #
###################

class Image(object):
  def __init__ (self, name):
    self.name = name
    self._features = []
    self._image_attrs = []

  def setImageAttribute (self, name, val):
    self._image_attrs.append((name, val))

  def _write (self, element):
    i = ET.SubElement(element, "{%s}image" % (Namespaces.VTS.name))
    i.attrib["name"] = self.name
    for feature in self._features:
      feature._write(i)
    for (name,val) in self._image_attrs:
      ae = ET.SubElement(i, "{%s}image-attribute" % (Namespaces.VTS))
      ae.attrib["name"] = name
      ae.attrib["value"] = str(val)
    return i

class SimpleDHCPImage(Image):
  def __init__ (self, subnet = None):
    super(SimpleDHCPImage, self).__init__("uh.simple-dhcpd")
    self.subnet = subnet

  def _write (self, element):
    e = super(SimpleDHCPImage, self)._write(element)
    if self.subnet:
      subnet = ET.SubElement(e, "{%s}image-attribute" % (Namespaces.VTS))
      subnet.attrib["name"] = "subnet"
      subnet.attrib["value"] = str(self.subnet)
    return e


class DatapathImage(Image):
  pass

class OVSImage(DatapathImage):
  def __init__ (self, name):
    super(OVSImage, self).__init__(name)

  @property
  def sflow (self):
    return None

  @sflow.setter
  def sflow (self, val):
    if isinstance(val, SFlow):
      self._features.append(val)
    # TODO: Throw exception

  @property
  def netflow (self):
    return None

  @netflow.setter
  def netflow (self, val):
    if isinstance(val, NetFlow):
      self._features.append(val)
    # TODO: Throw exception

  def setMirror (self, port):
    self._features.append(MirrorPort(port))


class OVSOpenFlowImage(OVSImage):
  def __init__ (self, controller, ofver = "1.0", dpid = None):
    super(OVSOpenFlowImage, self).__init__("bss:ovs-201-of")
    self.dpid = dpid
    self.controller = controller
    self.ofver = ofver

  def _write (self, element):
    i = super(OVSOpenFlowImage, self)._write(element)
    c = ET.SubElement(i, "{%s}controller" % (Namespaces.SDN.name))
    c.attrib["url"] = self.controller

    v = ET.SubElement(i, "{%s}openflow-version" % (Namespaces.VTS.name))
    v.attrib["value"] = self.ofver

    if self.dpid:
      d = ET.SubElement(i, "{%s}openflow-dpid" % (Namespaces.VTS.name))
      d.attrib["value"] = str(self.dpid)

    return i

class UnknownSTPModeError(Exception):
  def __init__ (self, val):
    self._val = val
  def __str__ (self):
    return "Unknown STP Mode (%d)" % (self._val)

class IllegalModeForParamError(Exception):
  def __init__ (self, param):
    self.param = param
  def __str__ (self):
    return "The parameter '%s' is not configurable in the current STP mode" % (self.param)

class OVSL2STP(object):
  STP = 1
  RSTP = 2

  def __init__ (self):
    self._mode = OVSL2STP.STP
    self._rstp_params = {}
    self._stp_params = {}

  @property
  def mode (self):
    return self._mode

  @mode.setter
  def mode (self, val):
    if val != OVSL2STP.STP and val != OVSL2STP.RSTP:
      raise UnknownSTPModeError(val)
    self._mode = val

  @property
  def type (self):
    if self._mode == OVSL2STP.STP:
      return "stp"
    elif self._mode == OVSL2STP.RSTP:
      return "rstp"

  @property
  def priority (self):
    try:
      return self._stp_params["priority"]
    except KeyError:
      return None

  @priority.setter
  def priority (self, val):
    self._stp_params["priority"] = val
    self._rstp_params["priority"] = val

  @property
  def max_age (self):
    try:
      return self._stp_params["max-age"]
    except KeyError:
      return None
    
  @max_age.setter
  def max_age (self, val):
    self._stp_params["max-age"] = val
    self._rstp_params["max-age"] = val

  @property
  def hello_time (self):
    if self._mode != OVSL2STP.STP:
      raise IllegalModeForParamError("hello-time")
    try:
      return self._stp_params["hello-time"]
    except KeyError:
      return None

  @hello_time.setter
  def hello_time (self, val):
    if self._mode != OVSL2STP.STP:
      raise IllegalModeForParamError("hello-time")
    self._stp_params["hello-time"] = val

  @property
  def forward_delay (self):
    try:
      return self._stp_params["forward-delay"]
    except KeyError:
      return None
    
  @forward_delay.setter
  def forward_delay (self, val):
    self._stp_params["forward-delay"] = val
    self._rstp_params["forward-delay"] = val

  @property
  def address (self):
    try:
      return self._stp_params["system-id"]
    except KeyError:
      return None

  @address.setter
  def address (self, val):
    self._stp_params["system-id"] = val
    self._rstp_params["address"] = val

  @property
  def ageing_time (self):
    if self._mode != OVSL2STP.RSTP:
      raise IllegalModeForParamError("ageing-time")
    try:
      return self._rstp_params["ageing-time"]
    except KeyError:
      return None

  @ageing_time.setter
  def ageing_time (self, val):
    if self._mode != OVSL2STP.RSTP:
      raise IllegalModeForParamError("ageing-time")
    self._rstp_params["ageing-time"] = val
    
  @property
  def xmit_hold_count (self):
    if self._mode != OVSL2STP.RSTP:
      raise IllegalModeForParamError("xmit-hold-count")
    try:
      return self._rstp_params["xmit-hold-count"]
    except KeyError:
      return None

  @xmit_hold_count.setter
  def xmit_hold_count (self, val):
    if self._mode != OVSL2STP.RSTP:
      raise IllegalModeForParamError("xmit-hold-count")
    self._rstp_params["xmit-hold-count"] = val

  def _write (self, element):
    se = ET.SubElement(element, "{%s}stp" % (Namespaces.VTS))

    if self._mode == OVSL2STP.STP:
      se.attrib["type"] = "stp"
      for k,v in self._stp_params.items():
        pe = ET.SubElement(se, "{%s}%s" % (Namespaces.VTS, k))
        pe.attrib["value"] = str(v)
    elif self._mode == OVSL2STP.RSTP:
      se.attrib["type"] = "rstp"
      for k,v in self._rstp_params.items():
        pe = ET.SubElement(se, "{%s}%s" % (Namespaces.VTS, k))
        pe.attrib["value"] = str(v)
    elif self._mode == -1:
      se.attrib["type"] = "disabled"

    return element

  def _as_jsonable (self):
    obj = {"type" : self.type}
    if self._mode == OVSL2STP.STP:
      for k,v in self._stp_params.items():
        obj[k] = v
    elif self._mode == OVSL2STP.RSTP:
      for k,v in self._rstp_params.items():
        obj[k] = v
    return obj

OVSL2STP.system_id = OVSL2STP.address

class OVSL2Image(OVSImage):
  def __init__ (self):
    super(OVSL2Image, self).__init__("bss:ovs-201")
    self.stp = OVSL2STP()
    self.mac_table_size = None
    self.mac_age = None

  def _write (self, element):
    i = super(OVSL2Image, self)._write(element)
    self.stp._write(i)
    mpe = ET.SubElement(i, "{%s}mac-table-params" % (Namespaces.VTS))
    if self.mac_table_size:
      mse = ET.SubElement(mpe, "{%s}max-size" % (Namespaces.VTS))
      mse.attrib["value"] = str(self.mac_table_size)
    if self.mac_age:
      mae = ET.SubElement(mpe, "{%s}max-age" % (Namespaces.VTS))
      mae.attrib["value"] = str(self.mac_age)
      
    return i



##################
# Image Features #
##################

class SFlow(object):
  def __init__ (self, collector_ip):
    self.collector_ip = collector_ip
    self.collector_port = 6343
    self.header_bytes = 128
    self.sampling_n = 64
    self.polling_secs = 5

  def _write (self, element):
    s = ET.SubElement(element, "{%s}sflow" % (Namespaces.VTS.name))
    s.attrib["collector"] = "%s:%d" % (self.collector_ip, self.collector_port)
    s.attrib["header-bytes"] = str(self.header_bytes)
    s.attrib["sampling-n"] = str(self.sampling_n)
    s.attrib["polling-secs"] = str(self.polling_secs)
    return s


class NetFlow(object):
  def __init__ (self, collector_ip):
    self.collector_ip = collector_ip
    self.collector_port = 6343
    self.timeout = 20

  def _write (self, element):
    s = ET.SubElement(element, "{%s}netflow" % (Namespaces.VTS))
    s.attrib["collector"] = "%s:%d" % (self.collector_ip, self.collector_port)
    s.attrib["timeout"] = str(self.timeout)
    return s

class MirrorPort(object):
  def __init__ (self, port):
    self.target = port.client_id

  def _write (self, element):
    s = ET.SubElement(element, "{%s}mirror" % (Namespaces.VTS))
    s.attrib["target"] = self.target
    return s

##################
# Graph Elements #
##################

class SSLVPNFunction(Resource):
  def __init__ (self, client_id):
    super(SSLVPNFunction, self).__init__()
    self.client_id = client_id
    self.protocol = None

  def _write (self, element):
    d = ET.SubElement(element, "{%s}function" % (Namespaces.VTS.name))
    d.attrib["client_id"] = self.client_id
    d.attrib["type"] = "sslvpn"
    return d

Request.EXTENSIONS.append(("SSLVPNFunction", SSLVPNFunction))
Request.EXTENSIONS.append(("L2SSLVPNServer", SSLVPNFunction))

class L2SSLVPNClient(Resource):
  def __init__ (self, client_id):
    super(L2SSLVPNClient, self).__init__()
    self.client_id = client_id
    self.protocol = "udp"
    self.remote_ip = None
    self.remote_port = None
    self.note = None
    self.key = None

  def _write (self, element):
    d = ET.SubElement(element, "{%s}function" % (Namespaces.VTS))
    d.attrib["type"] = "sslvpn-client"
    d.attrib["client_id"] = self.client_id
    d.attrib["remote-ip"] = str(self.remote_ip)
    d.attrib["remote-port"] = str(self.remote_port)
    d.attrib["note"] = str(self.note)
    d.text = str(self.key)
    return d

Request.EXTENSIONS.append(("L2SSLVPNClient", L2SSLVPNClient))


class Datapath(Resource):
  def __init__ (self, image, client_id):
    super(Datapath, self).__init__()
    if not isinstance(image, DatapathImage):
      raise BadImageTypeError(str(DatapathImage))
    self.image = image
    self.ports = []
    self.client_id = client_id

  @property
  def name (self):
    return self.client_id

  @name.setter
  def name (self, val):
    self.client_id = val

  def attachPort (self, port):
    if port.client_id is None:
      if port.name is None:
        port.client_id = "%s:%d" % (self.name, len(self.ports))
      else:
        port.client_id = "%s:%s" % (self.name, port.name)
    self.ports.append(port)
    return port

  def connectCrossSliver (self, other_dp):
    port = InternalCircuit(None, None, None, None)
    self.attachPort(port)
    port.target = other_dp.client_id
    return port

  def _write (self, element):
    d = ET.SubElement(element, "{%s}datapath" % (Namespaces.VTS.name))
    d.attrib["client_id"] = self.name
    self.image._write(d)
    for port in self.ports:
      port._write(d)
    return d

Request.EXTENSIONS.append(("Datapath", Datapath))


class Container(Resource):
  EXTENSIONS = []

  def __init__ (self, image, name):
    super(Container, self).__init__()
    self.image = image
    self.ports =[]
    self.name = name
    self.ram = None
    self.routes = []

    for name,ext in Container.EXTENSIONS:
      self._wrapext(name, ext)

  def attachPort (self, port):
    if port.name is None:
      port.client_id = "%s:%d" % (self.name, len(self.ports))
    else:
      port.client_id = "%s:%s" % (self.name, port.name)
    self.ports.append(port)
    return port

  def addIPRoute (self, network, gateway):
    self.routes.append((ipaddress.IPv4Network(six.ensure_text(network)),
                        ipaddress.IPv4Address(six.ensure_text(gateway))))

  def connectCrossSliver (self, other_dp):
    port = InternalCircuit(None, None, None, None)
    self.attachPort(port)
    port.target = other_dp.client_id
    return port

  def _write (self, element):
    d = ET.SubElement(element, "{%s}container" % (Namespaces.VTS.name))
    d.attrib["client_id"] = self.name
    if self.ram: d.attrib["ram"] = str(self.ram)
    self.image._write(d)
    for port in self.ports:
      port._write(d)
    for net,gw in self.routes:
      re = ET.SubElement(d, "{%s}route" % (Namespaces.VTS))
      re.attrib["network"] = str(net)
      re.attrib["gateway"] = str(gw)
    super(Container, self)._write(d)
    return d

Request.EXTENSIONS.append(("Container", Container))


class Port(object):
  def __init__ (self, name = None):
    self.client_id = None
    self.name = name

  def _write (self, element):
    p = ET.SubElement(element, "{%s}port" % (Namespaces.VTS.name))
    p.attrib["client_id"] = self.client_id
    return p


class PGCircuit(Port):
  def __init__ (self, name = None, delay_info = None):
    super(PGCircuit, self).__init__(name)
    self.delay_info = delay_info

  def _write (self, element):
    p = super(PGCircuit, self)._write(element)
    p.attrib["type"] = "pg-local"
    if self.delay_info:
      self.delay_info._write(p)
    return p

LocalCircuit = PGCircuit

class VFCircuit(Port):
  def __init__ (self, target):
    super(VFCircuit, self).__init__()
    self.target = target

  def _write (self, element):
    p = super(VFCircuit, self)._write(element)
    p.attrib["type"] = "vf-port"
    t = ET.SubElement(p, "{%s}target" % (Namespaces.VTS.name))
    t.attrib["remote-clientid"] = self.target
    return p


class InternalCircuit(Port):
  def __init__ (self, target, vlan = None, delay_info = None, loss_info = None):
    super(InternalCircuit, self).__init__()
    self.vlan = vlan
    self.target = target
    self.delay_info = delay_info
    self.loss_info = loss_info
    self.reorder_info = None

  def _write (self, element):
    p = super(InternalCircuit, self)._write(element)
    p.attrib["type"] = "internal"
    if self.vlan:
      p.attrib["vlan-id"] = str(self.vlan)
    if self.delay_info: self.delay_info._write(p)
    if self.loss_info: self.loss_info._write(p)
    if self.reorder_info: self.reorder_info._write(p)
    t = ET.SubElement(p, "{%s}target" % (Namespaces.VTS.name))
    t.attrib["remote-clientid"] = self.target
    return p


class ContainerPort(InternalCircuit):
  def __init__ (self, target, vlan = None, delay_info = None, loss_info = None):
    super(ContainerPort, self).__init__(target, vlan, delay_info, loss_info)
    self._v4addresses = []

  def _write (self, element):
    p = super(ContainerPort, self)._write(element)
    for addr in self._v4addresses:
      ae = ET.SubElement(p, "{%s}ipv4-address" % (Namespaces.VTS))
      ae.attrib["value"] = str(addr)
    return p

  def addIPv4Address (self, value):
    self._v4addresses.append(ipaddress.IPv4Interface(six.ensure_text(value)))


class GRECircuit(Port):
  def __init__ (self, circuit_plane, endpoint):
    super(GRECircuit, self).__init__()
    self.circuit_plane = circuit_plane
    self.endpoint = endpoint

  def _write (self, element):
    p = super(GRECircuit, self)._write(element)
    p.attrib["type"] = "gre"
    p.attrib["circuit-plane"] = self.circuit_plane
    p.attrib["endpoint"] = self.endpoint
    return p


######################
# Element Extensions #
######################

class Mount(Resource):
  def __init__ (self, type, name, mount_path):
    self.type = type
    self.name = name
    self.mount_path = mount_path
    self.attrs = {}

  def _write (self, element):
    melem = ET.SubElement(element, "{%s}mount" % (Namespaces.VTS))
    melem.attrib["type"] = self.type
    melem.attrib["name"] = self.name
    melem.attrib["path"] = self.mount_path
    for k,v in self.attrs.items():
      melem.attrib[k] = str(v)
    return melem

Container.EXTENSIONS.append(("Mount", Mount))


class HgMount(Mount):
  """ Clone a public mercurial repo on a host

  Args:
    name (str): a reference name given on the mounting AM, must be unique within a sliver
    source (str): the URL to the source of repository
    mount_path (str): the path where the repository would be mounted in the host filesystem
    branch (str): the branch of the repository to be cloned on host (if any)
  """
  def __init__ (self, name, source, mount_path, branch = "default"):
    super(HgMount, self).__init__("hg", name, mount_path)
    self.attrs["source"] = source
    self.attrs["branch"] = branch

Container.EXTENSIONS.append(("HgMount", HgMount))


class SecureHgMount(Mount):
  def __init__ (self, getversion_output, name, source, mount_path, branch = "default"):
    super(SecureHgMount, self).__init__("hg-secure", name, mount_path)
    self._source = source
    self.attrs["source"] = _am_encrypt(getversion_output, source)
    self.attrs["branch"] = branch

  def rebind (self, getversion_output):
    self.attrs["source"] = _am_encrypt(getversion_output, self._source)

Container.EXTENSIONS.append(("SecureHgMount", SecureHgMount))


class DropboxMount(Mount):
  def __init__ (self, name, mount_path):
    super(DropboxMount, self).__init__("dropbox", name, mount_path)

Container.EXTENSIONS.append(("DropboxMount", DropboxMount))


#############
# Utilities #
#############

def connectInternalCircuit (dp1, dp2, delay_info = None, loss_info = None):
  dp1v = None
  dp2v = None

  if isinstance(dp1, tuple):
    dp1v = dp1[1]
    dp1 = dp1[0]

  if isinstance(dp2, tuple):
    dp2v = dp2[1]
    dp2 = dp2[0]

  if isinstance(dp1, Container):
    sp = ContainerPort(None, dp1v, delay_info, loss_info)
  elif isinstance(dp1, Datapath):
    sp = InternalCircuit(None, dp1v, delay_info, loss_info)

  if isinstance(dp2, Container):
    dp = ContainerPort(None, dp2v, delay_info, loss_info)
  elif isinstance(dp2, Datapath):
    dp = InternalCircuit(None, dp2v, delay_info, loss_info)

  dp1.attachPort(sp)
  dp2.attachPort(dp)

  sp.target = dp.client_id
  dp.target = sp.client_id

  return (sp, dp)
