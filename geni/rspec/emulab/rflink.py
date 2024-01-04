# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from ..pg import Link, Request

#
# Class to hide the idiosynchrasies of PhantomNet RF links.
#
class RFLink(Link):
    def __init__(self, name):
        super(RFLink, self).__init__(name)
        self.bandwidth = 500
  
    def _write(self, root):
        lnk = super(RFLink, self)._write(root)
        lnk.attrib["protocol"] = "P2PLTE"
        return lnk

Request.EXTENSIONS.append(("RFLink", RFLink))
