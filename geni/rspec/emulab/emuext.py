# Copyright (c) 2016-2017 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Common set of RSpec extensions supported by many Emulab-based aggregates
"""

from __future__ import absolute_import

from ..pg import Request, Namespaces, Link, Node, Service, Command, RawPC
import geni.namespaces as GNS
from lxml import etree as ET

class setCollocateFactor(object):
    """Added to a top-level Request object, this extension limits the number
    of VMs from one experiment that Emulab will collocate on each physical
    host.
    """
    __ONCEONLY__ = True
    
    def __init__(self, mfactor):
        """mfactor is an integer, giving the maximum number of VMs to multiplex
        on each physical host."""
        self.mfactor = mfactor
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}collocate_factor" % (Namespaces.EMULAB.name))
        el.attrib["count"] = str(self.mfactor)
        return root

Request.EXTENSIONS.append(("setCollocateFactor", setCollocateFactor))

class setPackingStrategy(object):
    """Added to a top-level Request object, this extension controls the
    strategy used for distributing VMs across physical hosts
    """
    __ONCEONLY__ = True

    def __init__(self, strategy):
        self.strategy = strategy
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}packing_strategy" % (Namespaces.EMULAB.name))
        el.attrib["strategy"] = str(self.strategy)
        return root

Request.EXTENSIONS.append(("setPackingStrategy", setPackingStrategy))
    
class setRoutingStyle(object):
    """Added to a top-level Request object, this extension controls the
    routing that is automatically configured on the experiment (data-plane)
    side of the network.
    """
    __ONCEONLY__ = True
    
    def __init__(self, style):
        self.style = style
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}routing_style" % (Namespaces.EMULAB.name))
        el.attrib["style"] = str(self.style)
        return root

Request.EXTENSIONS.append(("setRoutingStyle", setRoutingStyle))

class setDelayImage(object):
    """Added to a top-level Request object, this extension sets the disk image
    that will be used for all delay nodes configured for the experiment.
    """
    __ONCEONLY__ = True
    
    def __init__(self, urn):
        """urn: URN of any image - to perform the intnded function, the 
        image must be capable of setting up bridging and/or traffic shaping.
        """
        self.urn = urn
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}delay_image" % (Namespaces.EMULAB.name))
        el.attrib["urn"] = str(self.urn)
        return root

Request.EXTENSIONS.append(("setDelayImage", setDelayImage))

class setForceShaping(object):
    """Added to a Link or LAN object, this extension forces Emulab link
    shaping to be enabled, even if it is not strictly necessary. This
    allows the link properties to be changed dynamically via the Emulab event
    system.
    """
    __ONCEONLY__ = True
    
    def __init__(self):
        self._enabled = True
    
    def _write(self, root):
        if self._enabled == False:
            return root
        el = ET.SubElement(root, "{%s}force_shaping" % (Namespaces.EMULAB.name))
        el.attrib["enabled"] = "true"
        return root

Link.EXTENSIONS.append(("setForceShaping", setForceShaping))

class setNoBandwidthShaping(object):
    """Added to a Link or LAN object, this extension forces Emulab link
    shaping to be disabled for bandwidth, even if it is necessary. This
    is ignored if the link must be shaped for other reason (delay, loss).
    """
    __ONCEONLY__ = True
    
    def __init__(self):
        self._enabled = True
    
    def _write(self, root):
        if self._enabled == False:
            return root
        el = ET.SubElement(root,
                           "{%s}force_nobwshaping" % (Namespaces.EMULAB.name))
        el.attrib["enabled"] = "true"
        return root

Link.EXTENSIONS.append(("setNoBandwidthShaping", setNoBandwidthShaping))

class setNoInterSwitchLinks(object):
    """Added to a Link or LAN object, this extension forces the Emulab mapper
    to disallow mapping a link in the request topology to an inter-switch
    link.  This allows users to require that specific nodes in their
    topology be attached to the same switch(es).
    """
    __ONCEONLY__ = True
    
    def __init__(self):
        self._enabled = True
    
    def _write(self, root):
        if self._enabled == False:
            return root
        el = ET.SubElement(root, "{%s}interswitch" % (Namespaces.EMULAB.name))
        el.attrib["allow"] = "false"
        return root

Link.EXTENSIONS.append(("setNoInterSwitchLinks", setNoInterSwitchLinks))

class setUseTypeDefaultImage(object):
    """Added to a node that does not specify a disk image, this extension
    forces Emulab to use the hardware type default image instead of the
    standard geni default image. Useful with special hardware that should
    run a special image.
    """
    __ONCEONLY__ = True
    
    def __init__(self):
        self._enabled = True
    
    def _write(self, root):
        if self._enabled == False:
            return root
        el = ET.SubElement(root, "{%s}use_type_default_image"
                           % (Namespaces.EMULAB.name))
        el.attrib["enabled"] = "true"
        return root

Node.EXTENSIONS.append(("setUseTypeDefaultImage", setUseTypeDefaultImage))

class setFailureAction(object):
    """Added to a node this extension will tell Emulab based aggregates to
    ignore errors booting this node when starting an experiment. This allows
    the experiment to proceed so that the user has time to debug."""
    __ONCEONLY__ = True
    
    def __init__(self, action):
        self.action = action
        self._enabled = True
    
    def _write(self, root):
        if self._enabled == False:
            return root
        el = ET.SubElement(root, "{%s}failure_action" % (Namespaces.EMULAB.name))
        el.attrib["action"] = self.action
        return root

Node.EXTENSIONS.append(("setFailureAction", setFailureAction))

#
# Emulab Program Agents.
#
class ProgramAgent(Service):
    """Add an Emulab Program Agent, which can be controlled via the Emulab
    event system. Optional argument 'directory' specifies where to invoke
    the command from. Optional argument 'onexpstart' says to invoke the
    command when the experiment starts (time=0 in event speak). This is
    different than the Execute service, which runs every time the node boots.
    """
    def __init__ (self, name, command, directory = None, onexpstart = False):
        super(ProgramAgent, self).__init__()
        self.name = name
        self.command = command
        self.directory = directory
        self.onexpstart = onexpstart

    def _write (self, element):
        exc = ET.SubElement(element,
                            "{%s}program-agent" % (Namespaces.EMULAB.name))
        exc.attrib["name"] = self.name
        if isinstance(self.command, Command):
            exc.attrib["command"] = self.command.resolve()
        else:
            exc.attrib["command"] = self.command
        if self.directory:
            exc.attrib["directory"] = self.directory
        if self.onexpstart:
            exc.attrib["onexpstart"] = "true"
        return exc

class InstantiateOn(object):
    """Added to a node to specify that it a Xen VM should be bound to
    (instantiated on) another node in the topology.  Argument is the
    node instance or the client id of another node in the topology.
    """
    class InvalidParent(Exception):
        def __init__ (self, parent):
            super(InstantiateOn.InvalidParent, self).__init__()
            self.parent = parent
            def __str__ (self):
                return "%s is not a Raw PC" % (self.parent.name)
    
    __ONCEONLY__ = True
    
    def __init__(self, parent):
        if isinstance(parent, Node):
            # Xen VMs have to be bound to a raw PC.
            if not isinstance(parent, RawPC):
                raise InvalidParent(parent)
            self._parent = parent.name
        else:
            # Allow plain name to be used. At the moment the NS converter
            # is not trying to order nodes, so the vhost might not be
            # first. 
            self._parent = parent
            
    def _write(self, root):
        if self._parent == None:
            return root
        el = ET.SubElement(root, "{%s}relation" % (GNS.REQUEST.name))
        el.attrib["type"] = "instantiate_on"
        el.attrib["client_id"] = self._parent
        return root

Node.EXTENSIONS.append(("InstantiateOn", InstantiateOn))

#
# A Bridged Link is syntatic sugar for two links separated by a bridge
# node acting as a delay node.
#
# Unfortunately, there is no way to get a handle on the parent object
# of an extension, so we need to get that explicitly.
#
class BridgedLink(object):
  """A bridged link is syntactic sugar used to create two links
separated by an Emulab delay (bridge) node. The BridgedLink class will
create the following topology:

	      left-link          right-link
	node1 =========== bridge ============ node2

The bridge is a special node type (sliver_type="delay") that tells the
CM to insert an Emulab delay node instead of a plain (router) node. A
delay node is a transparent Ethernet bridge between the left and right
segments above, but on which the traffic can be shaped wrt. bandwidth,
latency, and loss. For example:

        # Create the bridged link between the two nodes.
        link = request.BridgedLink("link")
        # Add two interfaces
        link.addInterface(iface1)
        link.addInterface(iface2)
        # Give the link (bridge) some shaping parameters.
        link.bandwidth = 10000
        link.latency   = 15
        link.plr       = 0.01"""

  # This tells the Request class to set the _parent member after creating the
  # object
  __WANTPARENT__ = True;
  
  def __init__ (self, name = None):
    if name is None:
      self.name = Link.newLinkID()
    else:
      self.name = name

    self.bridge_name = name + "_bridge"
    self.left_name   = name + "_left"
    self.right_name  = name + "_right"
    self.left_iface  = None
    self.right_iface = None

    self._bandwidth  = Link.DEFAULT_BW
    self._latency    = Link.DEFAULT_LAT
    self._plr        = Link.DEFAULT_PLR

    # This needs to get set with the setter; this helps us remember that we
    # have not been attached to a parent
    self.request = None

    # These will be set later when we know the parent
    self.bridge = None
    self.left_link = None
    self.right_link = None

  @property
  def _parent(self):
    return self.request

  @_parent.setter
  def _parent(self, request):
    self.request     = request
    self.bridge      = request.Bridge(self.bridge_name)
    self.left_link   = request.Link(self.left_name)
    self.left_link.addInterface(self.bridge.iface0);
    self.right_link  = request.Link(self.right_name)
    self.right_link.addInterface(self.bridge.iface1);

  def addInterface(self, interface):
      if self.left_iface == None:
          self.left_link.addInterface(interface)
          self.left_iface = interface
      else:
          self.right_link.addInterface(interface)
          self.right_iface = interface

  @property
  def bandwidth (self):
    return self._bandwidth

  @bandwidth.setter
  def bandwidth (self, val):
    self.bridge.pipe0.bandwidth = val;
    self.bridge.pipe1.bandwidth = val;
    self._bandwidth = val

  @property
  def latency (self):
    return self._latency

  @latency.setter
  def latency (self, val):
    self.bridge.pipe0.latency = val;
    self.bridge.pipe1.latency = val;
    self._latency = val

  @property
  def plr (self):
    return self._plr

  @plr.setter
  def plr (self, val):
    self.bridge.pipe0.lossrate = val;
    self.bridge.pipe1.lossrate = val;
    self._plr = val

  def _write(self, root):
      return root

Request.EXTENSIONS.append(("BridgedLink", BridgedLink))

class ShapedLink(BridgedLink):
  """A ShapedLink is a synonym for BridgedLink"""

  def __init__ (self, name = None):
    super(ShapedLink, self).__init__(name=name)

Request.EXTENSIONS.append(("ShapedLink", ShapedLink))
