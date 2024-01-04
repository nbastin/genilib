# Copyright (c) 2013  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json

import geni.rspec.pgmanifest as PGM

m = PGM.Manifest("vts-stage-manifest.xml")
for link in m.links:
  d = {"geni_sharelan_token" : "vts-segment-%s" % (link.client_id[4:]),
       "geni_sharelan_lanname" : link.client_id}
  f = open("%s.json" % (link.client_id), "w+")
  json.dump(d, f)
  f.close()
  
