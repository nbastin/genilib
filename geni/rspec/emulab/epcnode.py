# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from ..pg import RawPC, Execute, Request
from ..igext import XenVM
from .epcexc import InvalidRole
from .pndefs import EPCROLES, PNDEFS
from .emuext import ProgramAgent

#
# Defaults/constants used below
#
class _EPCDEFS(object):
    OEPC_STARTSCRIPT = "/opt/OpenEPC/bin/start_epc.sh"
    SUDOBIN = "/usr/bin/sudo"
    VM_RAM = 1024
    VALID_ROLES = (EPCROLES.ANY, EPCROLES.ENABLERS, EPCROLES.PGW, 
                   EPCROLES.SGW_MME_SGSN, EPCROLES.CLIENT, EPCROLES.ENODEB)

#
# Factory method for returning VM or raw node based on global setting.
# Settings class also allows users to set global image and hardware type
# for EPC nodes.
#
class EPCNodeFactorySettings(object):
    use_vm_nodes = False
    hardware_type = None
    disk_image = PNDEFS.DEF_BINOEPC_IMG
    do_sync_start = False

def mkepcnode(*args, **kwargs):
    node = None
    request = None
    if "request" in kwargs:
        request = kwargs["request"]
        del kwargs["request"]
    if EPCNodeFactorySettings.use_vm_nodes:
        if request:
            node = request.EPCVMNode(*args, **kwargs)
        else:
            node = EPCVMNode(*args, **kwargs)
    else:
        if request:
            node = request.EPCNode(*args, **kwargs)
        else:
            node = EPCNode(*args, **kwargs)
    if EPCNodeFactorySettings.hardware_type:
        node.hardware_type = EPCNodeFactorySettings.hardware_type
    if EPCNodeFactorySettings.disk_image:
        node.disk_image = EPCNodeFactorySettings.disk_image
    if EPCNodeFactorySettings.do_sync_start:
        node.syncstart = EPCNodeFactorySettings.do_sync_start
    return node

#
# Base EPC mixin node class.  This is the bulk of the implementation for
# both physical and VM node classes.
#
class _EPCBaseNode(object):
    def __init__ (self, client_id, role, hname = None, component_id = None,
                  prehook = None, posthook = None):
        if not role in _EPCDEFS.VALID_ROLES:
            raise InvalidRole(role)
        super(_EPCBaseNode, self).__init__(client_id, component_id = component_id)
        self.role = role
        self.hname = hname
        self.startscript = _EPCDEFS.OEPC_STARTSCRIPT
        self.prehook = prehook
        self.posthook = posthook
        self.syncstart = False

    def _write(self, root):
        startcmd = "%s %s -r %s" % (_EPCDEFS.SUDOBIN, self.startscript, 
                                    self.role)
        if self.hname:
            startcmd += " -h %s" % self.hname
        if self.prehook:
            startcmd += " -P %s" % self.prehook
        if self.posthook:
            startcmd += " -T %s" % self.posthook
        if self.syncstart:
            self.addService(ProgramAgent(self.client_id + '_epc0', startcmd, None, True))
        else:
            self.addService(Execute(shell="csh", command=startcmd))
        return super(_EPCBaseNode, self)._write(root)


#
# Physical EPC node class
#
class EPCNode(_EPCBaseNode,RawPC):
    pass

Request.EXTENSIONS.append(("EPCNode", EPCNode))


#
# VM EPC node class
#
class EPCVMNode(_EPCBaseNode,XenVM):
    def __init__ (self, client_id, role, hname = None, component_id = None,
                  prehook = None, posthook = None):
        super(EPCVMNode, self).__init__(client_id, role, hname, component_id, 
                                        prehook, posthook)
        self.exclusive = True # NEVER run on a shared host.
        self.disk = 0 # No thin provisioning when set!
        self.ram = _EPCDEFS.VM_RAM

Request.EXTENSIONS.append(("EPCVMNode", EPCVMNode))
