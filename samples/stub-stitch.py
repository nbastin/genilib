# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG
import geni.rspec.stitching as ST

DI_URL = "https://www.emulab.net/image_metadata.php?uuid=b21a466b-da48-11e4-97ea-38eaa71273fa"

r = PG.Request()

stub = PG.RawPC("stub")
stub.component_manager_id = "urn:publicid:IDN+instageni.gpolab.bbn.com+authority+cm"
stub_intf = stub.addInterface("if0")

r.addResource(stub)

real = PG.RawPC("raw-nps")
real.disk_image = DI_URL
real.component_manager_id = "urn:publicid:IDN+instageni.nps.edu+authority+cm"
real_intf = real.addInterface("if0")

r.addResource(real)

link = PG.StitchedLink("s-link")
link.addInterface(stub_intf)
link.addInterface(real_intf)
link.bandwidth = 1

r.addResource(link)

sd = ST.StitchInfo()
path = sd.addPath(ST.Path("s-link"))

h1 = path.addHop(ST.Hop())
h1.link_id = "urn:publicid:IDN+instageni.nps.edu+stitchport+procurve2:1.19.al2s"
h1.suggested_vlan = 1693

h2 = path.addHop(ST.Hop())
h2.link_id = "urn:publicid:IDN+al2s.internet2.edu+interface+sdn-sw.losa.net.internet2.edu:eth5/1:nps-ig"
h2.suggested_vlan = 1693

r.addResource(sd)

r.writeXML("test-stitch.xml")
