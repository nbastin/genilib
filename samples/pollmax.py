# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.util
import nbastin
import time

import geni.aggregate.instageni as IG

if __name__ == '__main__':
  context = nbastin.buildContext()

  while True:
    avail = geni.util.checkavailrawpc(context, IG.MAX)
    print "%s: %d" % (time.ctime(), len(avail))
    time.sleep(20)
