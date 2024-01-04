# Copyright (c) 2013  Barnstormer Softworks, Ltd

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class XMLContext(object):
  def __init__ (self, rspec, root, cur_elem = None):
    self.rspec = rspec
    self.root = root
    self.curelem = cur_elem
