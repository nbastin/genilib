# Copyright (c) 2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

class SLICE_ROLE(object):
  LEAD = "LEAD"
  ADMIN = "ADMIN"
  MEMBER = "MEMBER"
  OPERATOR = "OPERATOR"
  AUDITOR = "AUDITOR"

class PROJECT_ROLE(object):
  LEAD = "LEAD"
  ADMIN = "ADMIN"
  MEMBER = "MEMBER"

class REQCTX(object):
  PROJECT = 1
  SLICE = 2
  RESOURCE = 3
  SERVICE = 4
  MEMBER = 5

class REQSTATUS(object):
  PENDING = 0
  APPROVED = 1
  CANCELLED = 2
  REJECTED = 3
