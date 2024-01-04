# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from lxml import etree as ET

from ..pg import RawPC, Namespaces, Request
from .pndefs import PNDEFS

class UE(RawPC):
    def __init__ (self, client_id, component_id = None):
        super(UE, self).__init__(client_id, component_id = component_id)
        self.hardware_type = "ue"
        self.adb_target = None

    def _write (self, root):
        nd = super(UE, self)._write(root)
        if self.adb_target:
            tgt = ET.SubElement(nd, "{%s}adb_target" % (Namespaces.EMULAB.name))
            tgt.attrib["target_id"] = self.adb_target
        return nd

Request.EXTENSIONS.append(("UE", UE))
