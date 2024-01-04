# Copyright (c) 2015-2017  Barnstormer Softworks, Ltd.
# Copyright (c) 2020  University of Houston Networking Lab

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Utility types used within geni-lib."""

import binascii

import six

class DPID(object):
  """Utility class representing OpenFlow Datapath IDs

  This class tries to handle all likely inputs and desired outputs, while
  providing a single internal type to work with in the code.

  String representations passed in must be represented in hex, but may contain
  common separators (colon, dash, and period) in any configuration.

  Args:
    val (int, long, unicode, str)

  Raises:
    DPID.OutOfRangeError: If the DPID represented by `val` is larger than the spec allows
      or less than zero.
    DPID.InputTypeError: If `val` is not a supported data type
  """

  MAX = (2 ** 64) - 1

  class OutOfRangeError(Exception):
    def __init__ (self, val):
      super(DPID.OutOfRangeError, self).__init__()
      self.val = val
    def __str__ (self):
      return "Input value (%d) out of range of valid DPIDs" % (self.val)

  class InputTypeError(Exception):
    def __init__ (self, val):
      super(DPID.InputTypeError, self).__init__()
      self.val = val
    def __str__ (self):
      return "Input value (%s) has invalid type (%s)" % (self.val, type(self.val))

  def __init__ (self, val):
    self._dpid = None

    if isinstance(val, (six.string_types)):
      val = int(val.translate(None, ":-."), 16)

    if isinstance(val, (six.integer_types)):
      if val < DPID.MAX and val >= 0:
        self._dpid = val
      else:
        raise DPID.OutOfRangeError(val)
    else:
      raise DPID.InputTypeError(val)

  def __eq__ (self, other):
    return self._dpid == other._dpid # pylint: disable=W0212

  def __hash__ (self):
    return self._dpid

  def __str__ (self):
    """
    Returns:
      str: Hex formatted DPID, with colons
    """
    s = self.hexstr()
    return ":".join(["%s%s" % (s[x], s[x+1]) for x in range(0,15,2)])

  def __repr__ (self):
    return str(self)

  def __json__ (self):
    return str(self)

  def hexstr (self):
    """Unformatted hex representation of DPID

    Returns:
      str: Hex formatted DPID, without colons
    """
    return "%016x" % (self._dpid)

class EthernetMAC (object):
  """Utility class representing 48-bit Ethernet MAC Addresses

  This class tries to handle all likely inputs and desired outputs, while
  providing a single internal type to work with in the code.

  String representations passed in must be represented in hex, but may contain
  common separators (colon, dash, and period) in any configuration.

  Args:
    val (int, long, unicode, str)

  Raises:
    EthernetMAC.OutOfRangeError: If the MAC represented by `val` is larger than
      than 48-bits or less than zero.
    EthernetMAC.InputTypeError: If `val` is not a supported data type
  """

  MAX = 2 ** 48

  class OutOfRangeError(Exception):
    def __init__ (self, val):
      super(EthernetMAC.OutOfRangeError, self).__init__()
      self.val = val
    def __str__ (self):
      return "Input value (%d) out of range of valid Ethernet Addresses" % (self.val)

  class InputTypeError(Exception):
    def __init__ (self, val):
      super(EthernetMAC.InputTypeError, self).__init__()
      self.val = val
    def __str__ (self):
      return "Input value (%s) has invalid type (%s)" % (self.val, type(self.val))

  def __init__ (self, val):
    self._mac = None

    if isinstance(val, (six.string_types)):
      if len(val) == 6:
        val = binascii.hexlify(val)
      val = val.replace(":", "")
      val = val.replace("-", "")
      val = int(val, 16)

    if isinstance(val, (six.integer_types)):
      if val < EthernetMAC.MAX and val >= 0:
        self._mac = val
      else:
        raise EthernetMAC.OutOfRangeError(val)
    else:
      raise EthernetMAC.InputTypeError(val)

  def __eq__ (self, other):
    return self._mac == other._mac # pylint: disable=W0212

  def __hash__ (self):
    return self._mac

  def __str__ (self):
    """
    Returns:
      str: Hex formatted MAC, with colons
    """
    s = self.hexstr()
    return ":".join(["%s%s" % (s[x], s[x+1]) for x in range(0,11,2)])

  def __json__ (self):
    return str(self)

  def __repr__ (self):
    return str(self)

  def hexstr (self):
    """Unformatted hex representation of MAC

    Returns:
      str: Hex formatted MAC, without separators
    """
    return "%012x" % (self._mac)
