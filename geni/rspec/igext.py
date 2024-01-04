# Copyright (c) 2014-2020  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import re
import sys

from lxml import etree as ET
import six

from .. import namespaces as GNS
from .pg import Namespaces as PGNS
from .pg import Node
from .pg import Link
from .pg import Resource
from . import pg
from .. import urn

class OFController(object):
  """OpenFlow controller specification to be used on a PG VLAN.

Add to link objects using the Link.addChild() method.

.. note::
  This will have no effect if a trivial link is created by the aggregate.
  You need to make sure that a VLAN will be provisioned (typically by making sure
  that at least two interfaces on the link are on different physical hosts)."""

  def __init__ (self, host, port=6633):
    self.host = host
    self.port = port

  def _write (self, element):
    eof = ET.SubElement(element, "{%s}openflow_controller" % (PGNS.EMULAB))
    eof.attrib["url"] = "tcp:%s:%d" % (self.host, self.port)
    return eof


class XenVM(Node):
  """Xen-based Virtual Machine resource

  Args:
    client_id (str): Your name for this VM.  This must be unique within a single `Request` object.
    component_id (Optional[str]): The `component_id` of the site node you want to bind this VM to
    exclusive (Optional[bool]): Request this VM on an isolated host used only by your sliver.

  Attributes:
    cores (int): Number of CPU cores
    ram (int): Amount of memory in megabytes
    disk (int): Amount of disk space in gigabytes
    xen_ptype (str): Physical node type on which to instantiate the VM. Types are AM-specific.
  """
  def __init__ (self, client_id, component_id = None, exclusive = False):
    super(XenVM, self).__init__(client_id, "emulab-xen", component_id = component_id, exclusive = exclusive)
    self.cores = None
    self.ram = None
    self.disk = None
    self.xen_ptype = None

  def _write (self, root):
    nd = super(XenVM, self)._write(root)
    st = nd.find("{%s}sliver_type" % (GNS.REQUEST.name))
    if self.cores or self.ram or self.disk:
      xen = ET.SubElement(st, "{%s}xen" % (PGNS.EMULAB.name))
      if self.cores:
        xen.attrib["cores"] = str(self.cores)
      if self.ram:
        xen.attrib["ram"] = str(self.ram)
      if self.disk:
        xen.attrib["disk"] = str(self.disk)
    if self.xen_ptype is not None:
      pt = ET.SubElement(st, "{%s}xen_ptype" % (PGNS.EMULAB.name))
      pt.attrib["name"] = self.xen_ptype
    return nd

pg.Request.EXTENSIONS.append(("XenVM", XenVM))


class AddressPool(Resource):
  """A pool of public dynamic IP addresses belonging to a slice."""

  def __init__(self, name, count=1, type="any"):
    super(AddressPool, self).__init__()
    self.client_id = name
    self.count = count
    self.type = type
    self.component_manager_id = None

  @property
  def name (self):
    return self.client_id

  def _write (self, root):
    pl = ET.SubElement(root, "{%s}routable_pool" % (PGNS.EMULAB.name))
    pl.attrib["client_id"] = self.client_id
    if self.component_manager_id:
      pl.attrib["component_manager_id"] = self.component_manager_id

    pl.attrib["count"] = str(self.count)
    pl.attrib["type"] = self.type

    return pl

pg.Request.EXTENSIONS.append(("AddressPool", AddressPool))


class Blockstore(object):
  def __init__ (self, name, mount = None):
    """Creates a BlockStore object with the given name (arbitrary) and mountpoint."""
    self.name = name
    self.mount = mount
    self._size = None
    self.where = "local"    # local|remote
    self.readonly = False
    self.placement = "any"  # any|sysvol|nonsysvol
    self.dataset = None
    self.rwclone = False    # Only for remote blockstores.

  @property
  def size (self):
    return self._size

  @size.setter
  def size (self, val):
    match = re.match(r"^(\d+)GB$", val)
    if match:
      self._size = int(match.group(1))
    else:
      self._size = int(val)

  def _write (self, element):
    bse = ET.SubElement(element, "{%s}blockstore" % (PGNS.EMULAB))
    bse.attrib["name"] = self.name
    if self.mount:
      bse.attrib["mountpoint"] = self.mount
    bse.attrib["class"] = self.where
    if self._size:
      bse.attrib["size"] = "%dGB" % (self._size)
    bse.attrib["placement"] = self.placement
    if self.readonly:
      bse.attrib["readonly"] = "true"
    if self.rwclone:
      bse.attrib["rwclone"] = "true"
    if self.dataset:
      if isinstance(self.dataset, (six.string_types)):
        bse.attrib["dataset"] = self.dataset
      elif isinstance(self.dataset, urn.Base):
        bse.attrib["dataset"] = str(self.dataset)
    return bse

pg.Node.EXTENSIONS.append(("Blockstore", Blockstore))


class RemoteBlockstore(pg.Node):
  def __init__ (self, name, mount = None, ifacename = "if0"):
    super(RemoteBlockstore, self).__init__(name, "emulab-blockstore")
    bs = Blockstore(self.name, mount)
    bs.where = "remote"
    self._bs = bs
    self._interface = self.addInterface(ifacename)

  def _write (self, element):
    return self._bs._write(super(RemoteBlockstore, self)._write(element))

  @property
  def interface (self):
    return self._interface

  @property
  def size (self):
    return self._bs.size

  @size.setter
  def size (self, val):
    self._bs.size = val

  @property
  def mountpoint (self):
    return self._bs.mount

  @mountpoint.setter
  def mountpoint (self, val):
    self._bs.mount = val

  @property
  def readonly (self):
    return self._bs.readonly

  @readonly.setter
  def readonly (self, val):
    self._bs.readonly = val

  @property
  def rwclone (self):
    return self._bs.rwclone

  @rwclone.setter
  def rwclone (self, val):
    self._bs.rwclone = val

  @property
  def placement (self):
    return self._bs.placement

  @placement.setter
  def placement (self, val):
    self._bs.placement = val

  @property
  def dataset (self):
    return self._bs.dataset

  @dataset.setter
  def dataset (self, val):
    self._bs.dataset = val

pg.Request.EXTENSIONS.append(("RemoteBlockstore", RemoteBlockstore))

class Bridge(pg.Node):
  class Pipe(object):
    def __init__ (self):
      self.bandwidth = 0
      self.latency   = 0
      self.lossrate  = 0.0

  def __init__ (self, name, if0name = "if0", if1name = "if1"):
    super(Bridge, self).__init__(name, "delay")
    self.addNamespace(PGNS.DELAY)

    self.iface0 = self.addInterface(if0name)
    self.pipe0  = self.Pipe()
    self.iface1 = self.addInterface(if1name)
    self.pipe1  = self.Pipe()

  def _write (self, root):
    nd = super(Bridge, self)._write(root)
    st = nd.find("{%s}sliver_type" % (GNS.REQUEST.name))
    delay = ET.SubElement(st, "{%s}sliver_type_shaping" % (PGNS.DELAY.name))
    pipe0 = ET.SubElement(delay, "{%s}pipe" % (PGNS.DELAY.name))
    pipe0.attrib["source"]    = self.iface0.name
    pipe0.attrib["dest"]      = self.iface1.name
    pipe0.attrib["capacity"]  = str(self.pipe0.bandwidth)
    pipe0.attrib["latency"]   = str(self.pipe0.latency)
    pipe0.attrib["lossrate"]  = str(self.pipe0.lossrate)
    pipe1 = ET.SubElement(delay, "{%s}pipe" % (PGNS.DELAY.name))
    pipe1.attrib["source"]    = self.iface1.name
    pipe1.attrib["dest"]      = self.iface0.name
    pipe1.attrib["capacity"]  = str(self.pipe1.bandwidth)
    pipe1.attrib["latency"]   = str(self.pipe1.latency)
    pipe1.attrib["lossrate"]  = str(self.pipe1.lossrate)
    return nd

  # pipe0 goes with iface0, and pipe1 goes with iface1
  def getPipe (self, interface):
    if self.iface0.name is interface:
      return self.pipe0
    else:
      return self.pipe1

pg.Request.EXTENSIONS.append(("Bridge", Bridge))

class Firewall(object):
  class Style(object):
    OPEN     = "open"
    CLOSED   = "closed"
    BASIC    = "basic"

  class Direction(object):
    INCOMING = "incoming"
    OUTGOING = "outgoing"

  def __init__ (self, style):
    self.style = style
    self.exceptions = []

  def addException(self, port, direction, ip = None):
    self.exceptions.append({"port" : port, "direction" : direction, "ip" : ip})

  def _write (self, node):
    fw = ET.SubElement(node, "{%s}firewall" % (PGNS.EMULAB))
    fw.attrib["style"] = self.style
    for excep in self.exceptions:
      ex = ET.SubElement(fw, "exception")
      ex.attrib["port"]      = str(excep["port"])
      ex.attrib["direction"] = excep["direction"]
      if excep["ip"]:
        ex.attrib["ip"] = excep["ip"]
    return fw

XenVM.EXTENSIONS.append(("Firewall", Firewall))


class Tour(object):
  TEXT = "text"
  MARKDOWN = "markdown"

  # One or more blank lines, followed by "Instructions:" on it's own line, then
  # zero or more blank lines. Eats the blank lines.
  SPLIT_REGEX = re.compile(r"\n+^\w*instructions\w*:?\w*$\n+",
                           re.IGNORECASE | re.MULTILINE)

  class Step(object):
    # Duplicated because of the awkwardness of accessing class variables in
    # outer class
    TEXT = "text"
    MARKDOWN = "markdown"
    def __init__(self, target, description,
        steptype = None, description_type = MARKDOWN):
      if hasattr(target,'client_id'):
        self.id = target.client_id
      else:
        self.id = str(target)

      if steptype:
        self.type = steptype
      elif isinstance(target, Node):
        self.type = "node"
      elif isinstance(target, Link):
        self.type = "link"
      else:
        self.type = "node"

      self.description = description
      self.description_type = description_type

    def _write (self, root):
      stepel = ET.SubElement(root, "step")
      stepel.attrib["point_type"] = self.type
      stepel.attrib["point_id"]   = self.id
      desc = ET.SubElement(stepel, "description")
      desc.text = self.description
      desc.attrib["type"] = self.description_type

  def __init__ (self):
    self.description = None
    # Type can markdown
    self.description_type = Tour.TEXT
    self.instructions = None
    # Type can markdown
    self.instructions_type = Tour.TEXT
    self.steps = []

  def addStep(self, step):
    self.steps.append(step)

  def Description(self, type, desc):
    self.description_type = type
    self.description = desc

  def Instructions(self, type, inst):
    self.instructions_type = type
    self.instructions = inst

  def useDocstring(self, module = None):
    if module is None:
      module = sys.modules["__main__"]
    if not self.description and module.__doc__:
      docstr = module.__doc__
      docparts = Tour.SPLIT_REGEX.split(docstr,2)
      self.Description(Tour.MARKDOWN,docparts[0])
      if len(docparts) == 2 and not self.instructions:
        self.Instructions(Tour.MARKDOWN,docparts[1])
      return True
    else:
      return False

  def _write (self, root):
    #
    # Please do it this way, until some of our JS code is fixed.
    #
    td = ET.SubElement(root, "rspec_tour",
                       nsmap={None : PGNS.TOUR.name})
    if self.description:
      desc = ET.SubElement(td, "description")
      desc.text = self.description
      desc.attrib["type"] = self.description_type
    if self.instructions:
      inst = ET.SubElement(td, "instructions")
      inst.text = self.instructions
      inst.attrib["type"] = self.instructions_type
    if self.steps:
      steps = ET.SubElement(td, "steps")
      for step in self.steps:
        step._write(steps)
    return td


class ParameterData(object):
  def __init__ (self, parameters):
    self.parameters = parameters

  def _write (self, root):
    td = ET.SubElement(root, "data_set",
                       nsmap={None : PGNS.PARAMS.name})
    for param in self.parameters:
      that = self.parameters[param]
      if 'hide' in that and that['hide'] is False:
        desc = ET.SubElement(td, "data_item")
        desc.attrib["name"] = that['prefix'] + param

        if isinstance(that['value'], ET._Element):
          desc.append(that['value'])
        else:
          desc.text = str(that['value'])

pg.Request.EXTENSIONS.append(("ParameterData", ParameterData))


class Site(object):
  def __init__ (self, id):
    self.id = id

  def _write (self, node):
    site = ET.SubElement(node, "{%s}site" % (PGNS.JACKS))
    site.attrib["id"] = self.id
    return site

pg.Node.EXTENSIONS.append(("Site", Site))
pg.Link.EXTENSIONS.append(("Site", Site))


class Desire(object):
  def __init__ (self, name, weight):
    self.name = name
    self.weight = weight

  def _write (self, node):
    fd = ET.SubElement(node, "{%s}fd" % (PGNS.EMULAB))
    fd.attrib["name"] = self.name
    fd.attrib["weight"] = str(self.weight)
    return fd

pg.Node.EXTENSIONS.append(("Desire", Desire))


class Password(Resource):
  """A declaration for a randomly generated password.

The portal will generate the password, encrypt it, and pass on the
encrypted value to the AM(s) and therefore the node(s)."""

  def __init__(self, name=None):
    super(Password, self).__init__()
    self.name = name

  def _write (self, root):
    pl = ET.SubElement(root, "{%s}password" % (PGNS.EMULAB.name))
    if self.name:
      pl.attrib["name"] = self.name

    return pl
