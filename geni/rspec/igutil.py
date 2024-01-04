# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


def shared_xen (node):
  if not node.exclusive:
    if "emulab-xen" in node.sliver_types:
      return True
  return False
