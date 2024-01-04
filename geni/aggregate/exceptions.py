# Copyright (c) 2016  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

class AMError(Exception):
  def __init__ (self, text, data = None):
    super(AMError, self).__init__()
    self.text = str(text)
    self.data = data
  def __str__ (self):
    return self.text

