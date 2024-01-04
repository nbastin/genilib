# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import geni.urn
import geni.aggregate.protogeni

#
# Static set of EPC roles
#
class EPCROLES(object):
    ANY          = "any"
    ENABLERS     = "epc-enablers"
    PGW          = "pgw"
    SGW_MME_SGSN = "sgw-mme-sgsn"
    CLIENT       = "epc-client"
    ENODEB       = "enodeb"

#
# Static set of EPC lans (recognized by PhantomNet setup code)
#
class EPCLANS(object):
    MGMT   = "mgmt"
    NET_A  = "net-a"
    NET_B  = "net-b"
    NET_C  = "net-c"
    NET_D  = "net-d"
    AN_LTE = "an-lte"

#
# Other global constants
#
class PNDEFS(object):
    PNET_AM = geni.aggregate.protogeni.UTAH_PG
    DEF_BINOEPC_IMG = geni.urn.Image(PNET_AM, "PhantomNet:UBUNTU12-64-BINOEPC")
