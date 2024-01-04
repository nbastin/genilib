# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

#
# Common EPC exception classes
#

class InvalidRole(Exception):
    def __init__(self, role):
        self.role = role
    def __str__(self):
        return "Warning: Invalid EPC role: %s" % role
