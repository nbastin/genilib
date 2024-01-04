# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class XPathXRange(object):
  def __init__ (self, xp, klass):
    self._data = xp
    self._klass = klass
  def __iter__ (self):
    for obj in self._data:
      yield self._klass._fromdom(obj)
  def __len__ (self):
    return len(self._data)
  def __getitem__ (self, idx):
    return self._klass._fromdom(self._data[idx])
