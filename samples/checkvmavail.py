# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import multiprocessing as MP
import time

import geni.aggregate.instageni as IG
import geni.util

context = geni.util.loadContext(key_passphrase = True)

OVERLOAD = 43

def query_aggregate (context, site, q):
  try:
    res = []
    ad = site.listresources(context)
    for node in ad.nodes:
      if not node.exclusive:
        try:
          if "emulab-xen" in node.sliver_types:
            res.append((node.component_id, node.hardware_types["pcvm"], "Xen"))
          else:
            res.append((node.component_id, node.hardware_types["pcvm"], "OpenVZ"))
        except:
          continue
    q.put((site.name, res))
  except Exception:
    q.put((site.name, ["OFFLINE"]))


def do_parallel ():
  q = MP.Queue()
  for site in IG.aggregates():
    p = MP.Process(target=query_aggregate, args=(context, site, q))
    p.start()

  while MP.active_children():
    time.sleep(0.5)

  l = []
  while not q.empty():
    l.append(q.get())

  xen_used = xen_avail = xen_total = 0
  vz_avail = vz_total = 0

  overload_cids = []
  underload_cids = []

  for idx,pair in enumerate(l):
    site_vz = site_xen = 0
    entries = []

    (site_name, res) = pair
    try:
      for (cid, count, typ) in res:
        if typ == "Xen":
          used = 57 - int(count)
          site_xen += used
          if used >= OVERLOAD:
            overload_cids.append((cid, used))
          else:
            underload_cids.append((cid, used))
          xen_avail += int(count)
          xen_used += used
          xen_total += 57
        elif typ == "OpenVZ":
          site_vz += 100 - int(count)
          vz_avail += int(count)
          vz_total += 100
        entries.append("   [%s] %s/57 (%s)" % (cid, count, typ))
    except Exception:
      print res
    print "%02d %s (Used: %d Xen, %d OpenVZ)" % (idx+1, site_name, site_xen, site_vz)
    for entry in entries:
      print entry

  print "Used"
  print "----"
  print "OpenVZ: %d/%d" % (vz_avail, vz_total)
  print "Xen: %d/%d" % (xen_used, xen_total)
  print 

  print "Overloaded hosts: %d" % (len(overload_cids))
  print "Underloaded hosts: %d" % (len(underload_cids))

  for cid,used in overload_cids:
    print "%02d - %s" % (used, cid)

if __name__ == '__main__':
  do_parallel()
