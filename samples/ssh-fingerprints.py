#!/usr/bin/env python

# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import argparse
import hashlib
import base64

import geni.util
from geni.aggregate.frameworks import ClearinghouseError

def parse_args ():
  parser = argparse.ArgumentParser()
  parser.add_argument('--project', dest="project", default=None)
  args = parser.parse_args()
  return args

def main (opts):
  context = geni.util.loadContext(key_passphrase=True)
  if opts.project:
    context.project = opts.project

  members = context.cf.listProjectMembers(context)
  key_data = {}
  for member in members:
    try:
      key_data[member.urn] = context.cf.lookupSSHKeys(context, member.urn)
    except ClearinghouseError:
      key_data[member.urn] = None

  for urn,pklist in key_data.items():
    if not pklist:
      print "[%s] No Clearinghouse Response (possibly not in a slice)" % (urn)
      continue

    sigs = []
    for pk in pklist:
      if not pk.strip():
        continue
      b64data = pk.split()[1]
      raw_data = base64.b64decode(b64data)
      mdh = hashlib.md5(raw_data)
      s = mdh.hexdigest()
      sigs.append(":".join(["%s%s" % (s[x], s[x+1]) for x in xrange(0, len(s), 2)]))
    print "[%s] %s" % (urn, ", ".join(sigs))

if __name__ == '__main__':
  opts = parse_args()
  main(opts)
