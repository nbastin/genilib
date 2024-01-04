#!/usr/bin/env python

# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import multiprocessing as MP
from argparse import ArgumentParser
import time
import getpass

import geni.util
import geni.aggregate.instageni as IG

def get_advertisement (context, site):
  try:
    ad = site.listresources(context)
    f = open("%s-ad.xml" % (site.name), "w+")
    f.write(ad.text)
    f.close()
    print "[%s] Done" % (site.name)
  except Exception, e:
    print "[%s] OFFLINE" % (site.name)
  

def do_parallel ():
  context = geni.util.loadContext(key_passphrase=True)
  for idx,site in enumerate(IG.aggregates()):
    p = MP.Process(target=get_advertisement, args=(context, site))
    p.start()

  while MP.active_children():
    time.sleep(1)

if __name__ == '__main__':
  do_parallel()
