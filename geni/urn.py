# Copyright (c) 2014-2017 The University of Utah and Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Simple library for manipulating URNs, particularly those used for GENI
objects"""

from __future__ import absolute_import

import re

from geni.aggregate.core import AM
from geni.exceptions import WrongNumberOfArgumentsError

def Make(s):
  """Returns the 'most specific' URN object that it can for the given string.

  Specifically, returns a GENI URN if the string is in GENI format, or a Base
  URN if it is not.  May throw a MalformedURNError exception if the string is not a
  valid URN at all."""
  if GENI.isValidGENIURN(s):
    return GENI(s)
  return Base(s)

class MalformedURNError(Exception):
  """Exception indicating that a string is not a proper URN."""

  def __init__ (self, val):
    super(MalformedURNError, self).__init__()
    self._val = val

  def __str__(self):
    return "Malformed URN: %s" % self._val

class Base (object):
  """Base class representing any URN (RFC 2141)."""

  PREFIX = "urn"

  NID_PATTERN = "[a-z0-9][a-z0-9-]{0,31}"
  NSS_PATTERN = r"""[a-z0-9()+,\-.:=@;$_!*'%/?#]+"""
  NID_REGEX = re.compile("^%s$" % NID_PATTERN, re.IGNORECASE)
  NSS_REGEX = re.compile("^%s$" % NSS_PATTERN, re.IGNORECASE)
  URN_REGEX = re.compile("^urn:%s:%s$" % (NID_PATTERN, NSS_PATTERN),
                         re.IGNORECASE)

  @staticmethod
  def isValidURN(s):
    """Returns True if the string is a valid URN, False if not."""
    return Base.URN_REGEX.match(s) is not None

  @staticmethod
  def isValidNID(s):
    """Returns True if the string is a valid NID, False if not."""
    return Base.NID_REGEX.match(s) is not None

  @staticmethod
  def isValidNSS(s):
    """Returns True if the string is a valid NSS, False if not."""
    return Base.NSS_REGEX.match(s) is not None

  @staticmethod
  def _fromStr(s):
    if not Base.isValidURN(s):
      raise MalformedURNError(s)
    return tuple(re.split(":",s,2))

  def __init__ (self, *args):
    """Create a new generic URN

    URNs can be initialized in one of two ways:

    1) Passing a single string in URN format ('urn:NID:NSS')

    2) Passing two strings (the NID and the NSS) separately"""
    if len(args) == 1:
      # Note, _fromStr will thrown an exception if malformed
      (_, self._nid, self._nss) = Base._fromStr(args[0])
    elif len(args) == 2:
      if not Base.isValidNID(args[0]):
        raise MalformedURNError("NID: %s" % args[0])
      if not Base.isValidNSS(args[1]):
        raise MalformedURNError("NSS: %s" % args[1])
      self._nid = args[0]
      self._nss = args[1]
    else:
      raise WrongNumberOfArgumentsError()

  def __str__ (self):
    return "%s:%s:%s" % (Base.PREFIX, self._nid, self._nss)

  __repr__ = __str__

class GENI (Base):
  """Class representing the URNs used by GENI, which use the publicid NID and
  IDN (domain name) scheme, then impose some additional strucutre."""

  NID = "publicid"
  NSSPREFIX = "IDN"

  # Taken from the list at http://www.protogeni.net/wiki/URNs
  TYPE_AUTHORITY = "authority"  #: Aggregate Managers, Slice Authorities, etc.
  TYPE_IMAGE     = "image"      #: Disk images
  TYPE_INTERFACE = "interface"  #: Network interfaces
  TYPE_LINK      = "link"       #: Point-to-point and multipoint links
  TYPE_NODE      = "node"       #: Physical and virtual machines
  TYPE_SLICE     = "slice"      #: Container for allocated resources
  TYPE_SLIVER    = "sliver"     #: Slice of a specific resource
  TYPE_USER      = "user"       #: Principal

  # We use IDN for authorities, and many identifiers turn into parts of domain
  # names, so we sort of match against DNS strings (though are somewhat more
  # permissive)
  DNS_PART          = "[a-z0-9]+[a-z0-9-]*"
  DNS_FULL          = r"""(%s.?)+""" % DNS_PART

  AUTHORITY_PATTERN = "%s(:%s)*" % (DNS_FULL, DNS_FULL)
  TYPE_PATTERN      = DNS_PART
  NAME_PATTERN      = Base.NSS_PATTERN
  GENINSS_PATTERN   = r"""%s\+%s\+(?P<type>%s)\+%s""" % (NSSPREFIX, AUTHORITY_PATTERN,
                                                         TYPE_PATTERN, NAME_PATTERN)
  GENIURN_PATTERN   = "%s:%s:%s" % (Base.PREFIX, NID, GENINSS_PATTERN)

  AUTHORITY_REGEX   = re.compile("^%s$" % AUTHORITY_PATTERN, re.IGNORECASE)
  TYPE_REGEX        = re.compile("^%s$" % TYPE_PATTERN, re.IGNORECASE)
  NAME_REGEX        = re.compile("^%s$" % NAME_PATTERN, re.IGNORECASE)
  GENINSS_REGEX     = re.compile("^%s$" % GENINSS_PATTERN, re.IGNORECASE)
  GENIURN_REGEX     = re.compile("^%s$" % GENIURN_PATTERN, re.IGNORECASE)

  def __init__ (self, *args):
    """Create a URN in the format used for GENI objects

    There are four forms of this constructor:

    1) Pass a single string in GENI URN format ('urn:publicid:IDN+auth+type+name')

    2) Pass three arguments: the authority (a single string), the type (see the
       TYPE_ variables in this class), and the object name

    3) Pass three arguments: as #2, but the authorit(ies) are passed as a list,
       with the top-level authority coming first, followed by any subauthorities

    4) Pass three arguments: as #2, but the authority is a
       geni.aggregate.core.AM object, and the authority is taken from that
       object"""
    if len(args) == 1:
      # Superclass constructor parses and sets self._nss, which we then split
      # into its constituent GENI parts. _splitNSS might throw an exception.
      super(GENI,self).__init__(args[0])
      self._authorities, self._type, self._name = GENI._splitNSS(self._nss)
    elif len(args) == 3:
      if isinstance(args[0],str):
        # They gave us a string, figure out if it might have subauthorities
        # in it
        self._authorities = GENI._splitAuthorities(args[0])
      elif isinstance(args[0], AM):
        # If given an AM, extract its authority information; accept either a
        # proper URN object or a simple string
        if isinstance(args[0].component_manager_id, GENI):
          self._authorities = args[0].component_manager_id.authorities
        else:
          self._authorities = GENI(args[0].component_manager_id).authorities
      else:
        self._authorities = args[0]

      self._type = args[1]
      self._name = args[2]

      # Check if everything we got was well formed
      for authority in self._authorities:
        if not GENI.isValidAuthority(authority):
          raise MalformedURNError("Authority: %s" % authority)
      if not GENI.isValidType(self._type):
        raise MalformedURNError("Type: %s" % self._type)
      if not GENI.isValidName(self._name):
        raise MalformedURNError("Name: %s" % self._name)

      # In this form we have to reconstruct the NSS from all of the info we just
      # collected
      super(GENI,self).__init__(GENI.NID,self._makeNSS())
    else:
      raise WrongNumberOfArgumentsError()

  @property
  def authorities(self):
    """Returns a list containing at least one authority string (the top level
    authority) and possibly additional subauthorities."""
    return self._authorities

  @property
  def authority(self):
    """Return a single string capturing the entire authority/subauthority chain"""
    return ":".join(self._authorities)

  @property
  def name(self):
    """Returns the 'name' part of a GENI URN."""
    return self._name

  @property
  def type(self):
    """Returns the 'type' part of a GENI URN."""
    return self._type

  def _makeNSS(self):
    return "%s+%s+%s+%s" % (GENI.NSSPREFIX, self.authority, self._type,
                            self._name)

  @staticmethod
  def _splitNSS(s):
    if not GENI.isValidGENINSS(s):
      raise MalformedURNError("GENI NSS: %s" % s)
    matches = re.split(r"""\+""",s,4)
    return (GENI._splitAuthorities(matches[1]), matches[2], matches[3])

  @staticmethod
  def _splitAuthorities(s):
    parts = re.split(":",s)
    for part in parts:
      if not GENI.isValidAuthority(part):
        raise MalformedURNError("GENI Authority: %s" % part)
    return re.split(":",s)

  @staticmethod
  def isValidGENINSS(s):
    return GENI.GENINSS_REGEX.match(s) is not None

  @staticmethod
  def isValidAuthority(s):
    return GENI.AUTHORITY_REGEX.match(s) is not None

  @staticmethod
  def isValidType(s):
    # Note that we don't actually check against the set of known types found
    # above, as it is not a closed set
    return GENI.TYPE_REGEX.match(s) is not None

  @staticmethod
  def isValidName(s):
    return GENI.NAME_REGEX.match(s) is not None

  @staticmethod
  def GENIURNType(s):
    """Returns the type of the object if the URN is a valid GENI URN, or
    None otherwise."""
    matches = GENI.GENIURN_REGEX.match(s)
    if matches is None:
      return None
    return matches.group("type")

  @staticmethod
  def isValidGENIURN(s):
    """Returns True if the given string is a valid URN in GENI format, False
    otherwise."""
    return GENI.GENIURNType(s) is not None

def Authority (authorities, name):
  """Create a new GENI URN with type 'authority'."""
  return GENI(authorities, GENI.TYPE_AUTHORITY, name)

def Interface (authorities, name):
  """Create a new GENI URN with type 'interface'."""
  return GENI(authorities, GENI.TYPE_INTERFACE, name)

def Image (authorities, name, version = None):
  """Create a new GENI URN with type 'image'."""
  if version is not None:
    constructed_name = "%s:%s" % (name, str(version))
  else:
    constructed_name = name
  return GENI(authorities, GENI.TYPE_IMAGE, constructed_name)

def Link (authorities, name):
  """Create a new GENI URN with type 'link'."""
  return GENI(authorities, GENI.TYPE_LINK, name)

def Node (authorities, name):
  """Create a new GENI URN with type 'node'."""
  return GENI(authorities, GENI.TYPE_NODE, name)

def Slice (authorities, name):
  """Create a new GENI URN with type 'slice'."""
  return GENI(authorities, GENI.TYPE_SLICE, name)

def Sliver (authorities, name):
  """Create a new GENI URN with type 'sliver'."""
  return GENI(authorities, GENI.TYPE_SLIVER, name)

def User (authorities, name):
  """Create a new GENI URN with type 'user'."""
  return GENI(authorities, GENI.TYPE_USER, name)

if __name__ == "__main__":
  # pylint: disable=wrong-import-position,wrong-import-order,global-statement
  # Lame unit tests
  import sys
  import geni.aggregate.instageni as IG

  errors = 0

  def check_urn (urn, value):
    global errors
    if str(urn) == value:
      sys.stdout.write("PASS")
    else:
      sys.stdout.write("FAIL")
      errors = errors + 1

    sys.stdout.write(" %s / %s\n" % (urn,value))

  def check_type(s, t):
    global errors
    urn = Make(s)
    if isinstance(urn, t):
      sys.stdout.write("PASS")
    else:
      sys.stdout.write("FAIL")
      errors = errors + 1

    sys.stdout.write(" %s / %s\n" % (urn,t.__name__))

  check_urn(Base("isbn","0553575384"),"urn:isbn:0553575384")
  check_urn(GENI("emulab.net","user","ricci"),
            "urn:publicid:IDN+emulab.net+user+ricci")
  check_urn(Base("urn:isbn:0140186255"),"urn:isbn:0140186255")
  check_urn(GENI("urn:publicid:IDN+emulab.net+user+jay"),
            "urn:publicid:IDN+emulab.net+user+jay")
  check_urn(GENI(IG.Kentucky,"user","hussam"),
            "urn:publicid:IDN+lan.sdn.uky.edu+user+hussam")
  check_urn(Image(IG.UtahDDC,"UBUNTU64-STD"),
            "urn:publicid:IDN+utahddc.geniracks.net+image+UBUNTU64-STD")
  check_urn(Image(IG.UtahDDC,"UBUNTU64-STD",42),
            "urn:publicid:IDN+utahddc.geniracks.net+image+UBUNTU64-STD:42")
  check_urn(User(IG.Clemson,"kwang"),
            "urn:publicid:IDN+instageni.clemson.edu+user+kwang")
  check_urn(GENI("wisc.cloudlab.us", "image", "ramcloud-PG0:hq6_ubuntu16.04_singlePC:0"),
            "urn:publicid:IDN+wisc.cloudlab.us+image+ramcloud-PG0:hq6_ubuntu16.04_singlePC:0")

  check_type("urn:isbn:0345371984",Base)
  check_type("urn:publicid:IDN+utahddc.geniracks.net+image+UBUNTU64-STD",GENI)
  check_type("urn:publicid:IDN+utahddc.geniracks.net+image+UBUNTU64-STD:42",GENI)

  sys.exit(errors)
