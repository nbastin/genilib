#!/usr/bin/env python

# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import multiprocessing as MP
from argparse import ArgumentParser
import time

import geni.aggregate.instageni as IG
import geni.util

context = geni.util.loadContext(key_passphrase = True)

def query_aggregate (context, site, q = None):
  try:
    ad = site.listresources(context)
    total = [node for node in ad.nodes if node.exclusive and "raw-pc" in node.sliver_types]
    avail = [node.component_id for node in ad.nodes if node.available and node.exclusive and "raw-pc" in node.sliver_types]
    out = "[%s] (%d/%d)" % (site.name, len(avail), len(total))
#    print "[%s] %s" % (site.name, ", ".join(avail))
  except Exception:
    out = "[%s] OFFLINE" % (site.name)
  if q:
    q.put(out)
  else:
    print out
  

def do_parallel ():
  q = MP.Queue()
  for idx,site in enumerate(IG.aggregates()):
    p = MP.Process(target=query_aggregate, args=(context, site, q))
    p.start()

  while MP.active_children():
    time.sleep(1)

  l = []
  while not q.empty():
    l.append(q.get())

  for idx,txt in enumerate(l):
    print "%02d %s" % (idx+1, txt)


def do_serial ():
  for idx, site in enumerate(IG.aggregates()):
    query_aggregate(context, site)


def parse_args ():
  parser = ArgumentParser()
  parser.add_argument("--parallel", dest="parallel", default = False, action='store_true')
  opts = parser.parse_args()
  return opts

if __name__ == '__main__':
  opts = parse_args()

  if opts.parallel:
    do_parallel()
  else:
    do_serial()
