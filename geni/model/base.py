# Copyright (c) 2013-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

class Image(object):
  def __init__ (self):
    self.id = None
    self.urn = None


class ImageRegistry(object):
  def __init__ (self):
    self._data = {}

  def register (self, manager, image):
    self._data.setdefault(image.id, {})[manager] = image
