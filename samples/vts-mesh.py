# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import itertools
import geni.rspec.vts as VTS

r = VTS.Request()

image = VTS.OVSOpenFlowImage("tcp:54.88.120.184:6633")
#image.sflow = VTS.SFlow("192.0.2.1")

# Create all the empty datapaths and add them to the Request
dps = [VTS.Datapath(image, "dp%d" % (x)) for x in xrange(0,6)]
for dp in dps:
  r.addResource(dp)

# Build the switch mesh
pairs = itertools.combinations(dps, 2)
for src,dst in pairs:
  VTS.connectInternalCircuit(src, dst)

# Add two host circuits
dps[0].attachPort(VTS.PGCircuit())
dps[1].attachPort(VTS.PGCircuit())

# Write out the XML
r.write("vts-mesh.xml")
