# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class AbstractImplementationError(Exception):
  def __str__ (self):
    return "Called unimplemented abstract method"

class NoUserError(Exception):
  def __str__ (self):
    return "No framework user specified"

class SliceCredError(Exception):
  def __init__ (self, text):
    super(SliceCredError, self).__init__()
    self.text = text

  def __str__ (self):
    return self.text

class WrongNumberOfArgumentsError(Exception):
  def __str__ (self):
    return "Called a function with the wrong number of arguments"
