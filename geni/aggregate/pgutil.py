# Copyright (c) 2016-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from .exceptions import AMError

# pylint: disable=multiple-statements
class ProtoGENIError(AMError): pass

class ResourceBusyError(ProtoGENIError): pass
class VLANUnavailableError(ProtoGENIError): pass
class InsufficientBandwidthError(ProtoGENIError): pass
class InsufficientNodesError(ProtoGENIError): pass
class InsufficientMemoryError(ProtoGENIError): pass
class NoMappingError(ProtoGENIError): pass
# pylint: enable=multiple-statements

def raiseError(res):
  amcode = res["code"]["am_code"]
  output = res["output"]
  if amcode == 14:
    e = ResourceBusyError(output, res)
  elif amcode == 24:
    e = VLANUnavailableError(output, res)
  elif amcode == 25:
    e = InsufficientBandwidthError(output, res)
  elif amcode == 26:
    e = InsufficientNodesError(output, res)
  elif amcode == 27:
    e = InsufficientMemoryError(output, res)
  elif amcode == 28:
    e = NoMappingError(output, res)
  else:
    e = ProtoGENIError(output, res)

  try:
    e.error_url = res["code"]["protogeni_error_url"]
  except KeyError:
    pass

  raise e
