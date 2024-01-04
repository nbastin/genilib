# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from ..pg import LAN, Request
from .pndefs import EPCLANS

#
# EPC lan class.  Convenience wrapper.
#
class EPClan(LAN):

    def __init__(self, name, vmlan = False):
        super(EPClan, self).__init__(name)
        if vmlan:
            self.vlan_tagging = 1
            self.trivial_ok = 1
            self.link_multiplexing = 1
        # Force mgmt lan to be best effort.
        if name == EPCLANS.MGMT:
            self.bandwidth = -1
            self.best_effort = 1

    def isMember(self, node):
        for intf in self.interfaces:
            if intf.node == node:
                return True
        return False

    def addMember(self, node, bandwidth = 0, latency = 0, plr = 0):
        intf = node.addInterface(self.client_id)
        if bandwidth:
            intf.bandwidth = bandwidth
        if latency:
            intf.latency = latency
        if plr:
            intf.plr = plr
        self.addInterface(intf)
        return intf

    def _write(self, root):
        if not self.bandwidth:
            self.bandwidth = -1
            self.best_effort = 1
        return super(EPClan, self)._write(root)

Request.EXTENSIONS.append(("EPClan", EPClan))
