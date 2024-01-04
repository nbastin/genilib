# Copyright (c) 2013  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from geni.model import base

class ComputeDiskImage(base.Image):
  def __init__ (self):
    super(ComputeDiskImage, self).__init__ ()
    self.url = None
    self.os = None
    self.osver = None
    self.arch = None

