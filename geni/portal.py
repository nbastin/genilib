# Copyright (c) 2014-2017 The University of Utah and Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Library for dealing with scripts that are run in the context of a portal."""

from __future__ import absolute_import

import sys
import os
import atexit
import warnings
import json
import argparse
from argparse import Namespace

import six

from .rspec import igext
from .rspec import pgmanifest
from .rspec.pg import Request

class ParameterType (object):
  """Parameter types understood by Context.defineParameter()."""

  INTEGER     = "integer"       #: Simple integer
  STRING      = "string"        #: Any string
  BOOLEAN     = "boolean"       #: True/False
  IMAGE       = "image"         #: URN specifying a particular image
  AGGREGATE   = "aggregate"     #: URN specifying an Aggregate Manger
  NODETYPE    = "nodetype"      #: String specifying a type of node
  BANDWIDTH   = "bandwidth"     #: Floating-point number to be used for bandwidth
  LATENCY     = "latency"       #: Floating-point number to be used for latency
  SIZE        = "size"          #: Integer for size (eg. MB, GB, etc.)
  PUBKEY      = "pubkey"        #: An RSA public key.
  LOSSRATE    = "lossrate"      #: Floating-point number 0.0 <= N < 1.0

  argparsemap = { INTEGER: int, STRING: str, BOOLEAN: bool, IMAGE: str,
                  AGGREGATE: str, NODETYPE: str, BANDWIDTH: float,
                  LATENCY: float, SIZE: int, PUBKEY: str, LOSSRATE: float }

class Parameter(object):
  UNSET = (-1, -2, -1)

  def __init__ (self):
    self.name = None
    self.description = None
    self.type = None
    self.defaultValue = None
    self.legalValues = None
    self.longDescription = None
    self.advanced = False
    self.hide = False
    self.prefix = "emulab.net.parameter."
    self.groupId = None

    self.is_set = False

  def __contains__ (self, key):
    return key in self.__dict__

  def __getitem__ (self, key):
    return self.__dict__[key]

  def __setitem__ (self, key, val):
    self.__dict__[key] = val


class Context (object):
  """Handle context for scripts being run inside a portal.

  This class handles context for the portal, including where to put output
  RSpecs and handling parameterized scripts.

  Scripts using this class can also be run "standalone" (ie. not by the
  portal), in which case they take parameters on the command line and put
  RSpecs on the standard output.

  This class is a singleton. Most programs should access it through the
  portal.context variable; any additional "instances" of the object will
  be references to this."""

  """This is a singleton class; only one can exist at a time

  This is implemented by overriding __new__"""
  _instance = None
  _initialized = False
  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      cls._instance = super(Context, cls).__new__(cls, *args, **kwargs)
    return cls._instance

  def __init__ (self):
    # If someone accidentally calls the constructor on the singleton, this
    # prevents us for wiping out its previous state
    if self.__class__._initialized:
      return

    self._request = None
    self._suppressAutoPrint = False
    self._parameters = {}
    self._parameterGroups = {}
    self._parameterOrder = []
    self._parameterErrors = []
    self._parameterWarnings = []
    self._parameterWarningsAreFatal = False
    self._bindingDone = False
    if 'GENILIB_PORTAL_MODE' in os.environ:
      self._standalone = False
      self._portalRequestPath = os.environ.get('GENILIB_PORTAL_REQUEST_PATH',None)
      self._dumpParamsPath = os.environ.get('GENILIB_PORTAL_DUMPPARAMS_PATH',None)
      self._readParamsPath = os.environ.get('GENILIB_PORTAL_PARAMS_PATH',None)
      self._parameterWarningsAreFatal = \
        bool(os.environ.get('GENILIB_PORTAL_WARNINGS_ARE_FATAL',None))
    else:
      self._standalone = True
      self._portalRequestPath = None
    self.__class__._initialized = True

  def bindRequestRSpec (self, rspec):
    """Bind the given request RSpec to the context, so that it can be
    automatically used with methods like printRequestRSpec.

    At the present time, only one request can be bound to a context"""
    if self._request is None:
      self._request = rspec
      # This feature removed until we can think through all the corner cases
      # better
      #sys.excepthook = self._make_excepthook()
      #atexit.register(self._autoPrintRequest)
    else:
      raise MultipleRSpecError

  def makeRequestRSpec (self):
    """Make a new request RSpec, bind it to this context, and return it"""
    rspec = Request()
    self.bindRequestRSpec(rspec)
    return rspec

  def printRequestRSpec (self, rspec = None):
    """Print the given request RSpec, or the one bound to this context if none
    is given.

    If run standalone (not in the portal), the request will be printed to the
    standard output; if run in the portal, it will be placed someplace the
    portal can pick it up.

    If the given rspec does not have a Tour object, this will attempt to
    build one from the file's docstring"""
    if rspec is None:
      if self._request is not None:
        rspec = self._request
      else:
        raise NoRSpecError("None supplied or bound to context")

    if not rspec.hasTour():
      tour = igext.Tour()
      if tour.useDocstring():
        rspec.addTour(tour)

    if any(self._parameters):
      rspec.ParameterData(self._parameters)

    self._suppressAutoPrint = True

    rspec.writeXML(self._portalRequestPath)

  def defineParameter (self, name, description, typ, defaultValue, legalValues = None,
                       longDescription = None, advanced = False, groupId = None, hide=False,
                       prefix="emulab.net.parameter."):
    """Define a new paramter to the script.

    The given name will be used when parameters are bound. The description is
    brief help text that will be shown to the user when making his/her selection. The
    type should be one of the types defined by ParameterType. defaultValue is
    required, but legalValues (a list) is optional; the defaultValue must be
    one of the legalValues. Entries in the legalValues list may be either
    simple strings (eg. "m400"), in which case they will be show directly to
    the user, or 2-element tuples (eg. ("m400", "ARM64"),), in which the second
    entry is what is shown to the user. defaultValue may be a tuple, so that
    one can pass, say, 'legalvalues[0]' for the option. The longDescription is
    an optional, detailed description of this parameter and how it relates to
    other parameters; it will be shown to the user if they ask to see the help,
    or as a pop-up/tooltip.  advanced, group, and groupName all provide parameter
    group abstractions.  Parameter groups are hidden by default from the user,
    and the user can expand them to view and modify them if desired.  By setting
    advanced to True, you create a parameter group named "Advanced Parameters";
    this group will not exist or be shown if none of your parameters set the
    'advanced' argument to True.

    After defining parameters, bindParameters() must be called exactly once."""

    if isinstance(defaultValue, tuple):
      defaultValue = defaultValue[0]

    if legalValues and defaultValue not in Context._legalList(legalValues):
      raise IllegalParameterDefaultError(defaultValue)

    self._parameterOrder.append(name)

    param = Parameter()
    param.name = name
    param.description = description
    param.type = typ
    param.defaultValue = defaultValue
    param.legalValues = legalValues
    param.longDescription = longDescription
    param.advanced = advanced
    param.hide = hide
    param.prefix = prefix

    if groupId is not None:
      param.groupId = groupId

    self._parameters[name] = param

    if len(self._parameters) == 1:
      atexit.register(self._checkBind)

  def defineParameterGroup(self, groupId, groupName):
    """
    Define a parameter group.  Parameters may be added to this group, which has
    an identifying token composed of alphanumeric characters (groupId), and a
    human-readable name (groupName).  Groups are intended to be used for advanced
    parameters; in the portal UI, they hidden in an expandable panel with the
    groupName --- and the user can choose to see and modify them, or not.  You
    do not need to specify any groups; you can simply stuff all your parameters
    into the "Advanced Parameters" group by setting the 'advanced' argument of
    defineParameter to True.  If you need multiple groups, define your own
    groups this way.
    """
    self._parameterGroups[groupId] = groupName

  def bindParameters (self,altParamSrc=None):
    """Returns values for the parameters defined by defineParameter().

    Returns a Namespace (like argparse), so if you call foo = bindParameters(), a
    parameter defined with name "bar" is accessed as foo.bar . Since defaults
    are required, all parameters are guaranteed to have values in the Namespace

    If run standaline (not in the portal), parameters are pulled from the command
    line (try running with --help); if run in the portal, they are pulled from
    the portal itself.  Or, if you provide the altParamSrc argument, you can
    specify your own parameters.  If altParamSrc is a dict, we will bind the
    params as a dict, using the keys as parameter names, and the values as
    parameter values.  If altParamSrc is a geni.rspec.pgmanifest.Manifest, we
    will extract the parameters and their values from the Manifest.  Finally,
    if altParamSrc is a string, we'll try to parse it as a PG manifest xml
    document.  No other forms of altParamSrc are currently specified."""
    self._bindingDone = True
    if altParamSrc:
      if isinstance(altParamSrc, dict):
        return self._bindParametersDict(altParamSrc)
      elif isinstance(altParamSrc, pgmanifest.Manifest):
        return self._bindParametersManifest(altParamSrc)
      elif isinstance(altParamSrc, (six.string_types)):
        try:
          manifestObj = pgmanifest.Manifest(xml=altParamSrc)
          return self._bindParametersManifest(manifestObj)
        except:
          ex = sys.exc_info()[0]
          raise ParameterBindError("assumed str altParamSrc was xml manifest, but"
                                   " parse error: %s" % (str(ex),))
      else:
        raise ParameterBindError("unknown altParamSrc type: %s"
                                 % (str(type(altParamSrc)),))
    elif self._standalone:
      return self._bindParametersCmdline()
    else:
      if self._dumpParamsPath:
        self._dumpParamsJSON()
      return self._bindParametersEnv()

  def makeParameterWarningsFatal (self):
    """
    Enable this option if you want to return an error to the user for
    incorrect parameter values, even if they can be autocorrected.  This can
    be useful to show the user that
    """
    self._parameterWarningsAreFatal = True

  def reportError (self,parameterError,immediate=False):
    """
    Report a parameter error to the portal.  @parameterError is an
    exception object of type ParameterError.  If @immediate is True,
    your script will exit immediately at this point with a dump of the
    errors (and fatal warnings, if enabled via
    Context.makeParameterWarningsFatal) in JSON format.  If @immediate
    is False, the errors will accumulate until Context.verifyParameters
    is called (and the errors will then be printed).
    """
    self._parameterErrors.append(parameterError)
    if immediate:
      self.verifyParameters()

  def reportWarning (self,parameterError):
    """
    Record a parameter warning.  Warnings will be printed if there are
    other errors or if warnings have been set to be fatal, when
    Context.verifyParameters() is called, or when there is another
    subsequent immediate error.
    """
    self._parameterWarnings.append(parameterError)

  def verifyParameters (self):
    """
    If there have been calls to Context.parameterError, and/or to
    Context.parameterWarning (and Context.makeParameterWarningsFatal has
    been called, making warnings fatal), this function will spit out some
    nice JSON-formatted exception info on stderr
    """
    if len(self._parameterErrors) == 0 \
      and (len(self._parameterWarnings) == 0 \
        or not self._parameterWarningsAreFatal):
      return 0

    #
    # Dump a JSON list of typed errors.
    #
    ea = []
    ea.extend(self._parameterErrors)
    ea.extend(self._parameterWarnings)
    json.dump(ea,sys.stderr,cls=PortalJSONEncoder)

    #
    # Exit with a count of errors and (fatal) warnings, added to 100 ...
    # try to distinguish ourselves meaningfully!
    #
    retcode = len(self._parameterErrors)
    if self._parameterWarningsAreFatal:
      retcode += len(self._parameterWarnings)
    sys.exit(100+retcode)

  def suppressAutoPrint (self):
    """
    Suppress the automatic printing of the bound RSpec that normally happens
    when the program exits.
    """
    self._suppressAutoPrint = True

  @staticmethod
  def _legalList(l):
    return [x if not isinstance(x, tuple) else x[0] for x in l]

  def _bindParametersCmdline (self):
    parser = argparse.ArgumentParser()
    for name in self._parameterOrder:
      opts = self._parameters[name]
      if opts['legalValues']:
        legal = Context._legalList(opts['legalValues'])
      else:
        legal = None
      if 'GENILIB_PARAMS_ASK' in os.environ:
        parser.add_argument("--" + name,
                            type    = ParameterType.argparsemap[opts['type']],
                            default = Parameter.UNSET,
                            choices = legal,
                            help    = opts['description'])
      else:
        parser.add_argument("--" + name,
                            type    = ParameterType.argparsemap[opts['type']],
                            default = opts['defaultValue'],
                            choices = legal,
                            help    = opts['description'])

    args = parser.parse_args()
    for name in self._parameterOrder:
      val = getattr(args, name)
      if val != Parameter.UNSET:
        self._parameters[name]['value'] = val
        self._parameters[name].is_set = True

    for name in self._parameterOrder:
      param = self._parameters[name]
      if param.is_set:
        continue

      while True:
        val = raw_input("%s (%s) [%s]: " % (param.description, param.type, str(param.defaultValue)))
        if val == "?":
          if param.longDescription:
            print param.longDescription
          else:
            print "No help available for this parameter"
        elif not val:
          val = param.defaultValue
          break
        else:
          break
      param.value = ParameterType.argparsemap[param.type](val)
      param.is_set = True

      setattr(args, name, param.value)

    return args

  def _bindParametersEnv (self):
    namespace = Namespace()
    paramValues = {}
    if self._readParamsPath:
      f = open(self._readParamsPath, "r")
      paramValues = json.load(f)
      f.close()
    for name in self._parameterOrder:
      opts = self._parameters[name]
      val = paramValues.get(name, opts['defaultValue'])
      try:
        val = ParameterType.argparsemap[opts['type']](val)
      except Exception:
        self.reportError(ParameterError("Could not coerce '%s' to '%s'" %
                                        (val, opts['type']), [name]))
        continue
      if opts['legalValues'] and val not in Context._legalList(opts['legalValues']):
        self.reportError(ParameterError("Illegal value '%s'" % (val,), [name]))
      else:
        setattr(namespace, name, val)
        self._parameters[name]['value'] = val
    # This might not return.
    self.verifyParameters()
    return namespace

  def _bindParametersDict(self,paramValues):
    namespace = Namespace()
    for name in self._parameterOrder:
      opts = self._parameters[name]
      val = paramValues.get(name, opts['defaultValue'])
      try:
        if type(opts['defaultValue']) == bool:
          if val == "False" or val == "false":
            val = False
          elif val == "True" or val == "true":
            val = True
          else:
            val = ParameterType.argparsemap[opts['type']](val)
        else:
          val = ParameterType.argparsemap[opts['type']](val)
      except:
        print "ERROR: Could not coerce '%s' to '%s'" % (val, opts['type'])
        continue
      if opts['legalValues'] and \
        val not in Context._legalList(opts['legalValues']):
        print "ERROR: Illegal value '%s'" % (val,),[name]
      else:
        setattr(namespace, name, val)
        self._parameters[name]['value'] = val
    # This might not return.
    self.verifyParameters()
    self._bindingDone = True
    return namespace

  def _bindParametersManifest(self,manifest):
    pdict = {}
    for manifestParameter in manifest.parameters:
      pdict[manifestParameter.name] = manifestParameter.value
    return self._bindParametersDict(pdict)

  def _dumpParamsJSON (self):
    #
    # Output the parameter dict in sorted order (sorted in terms of parameter
    # definition order).  This is correct, identical to json.dump (other than
    # key order), and much easier than subclassing json.JSONEncoder :).
    #
    didFirst = False
    f = open(self._dumpParamsPath, "w+")
    f.write('{')
    for name in self._parameterOrder:
      if didFirst:
        f.write(', ')
      else:
        didFirst = True
      opts = self._parameters[name]
      if "groupId" in opts and "groupId" in self._parameterGroups:
        opts['groupName'] = self._parameterGroups[opts['groupId']]
      json.dump(name,f)
      f.write(': ')
      json.dump(opts,f)
    f.write('}')
    f.close()
    return

  def _checkBind (self):
    if len(self._parameters) > 0 and not self._bindingDone:
      warnings.warn("Parameters were defined, but never bound with " +
                    " bindParameters()", RuntimeWarning)

  def _autoPrintRequest (self):
    if not self._suppressAutoPrint:
      self.printRequestRSpec()

  def _make_excepthook (self):
    old_excepthook = sys.excepthook
    def _excepthook(type, value, traceback):
      self.suppressAutoPrint()
      return old_excepthook(type, value, traceback)
    return _excepthook

context = Context()
"""
Module-global Context object - most users of this module should simply use
this rather than trying to create a new Context object
"""

def get_context():
  return context

class PortalJSONEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o,PortalError):
      return o.__objdict__()
    else:
      # First try the default encoder:
      try:
        return json.JSONEncoder.default(self, o)
      except Exception:
        try:
          # Then try to return a string, at least
          return str(o)
        except Exception:
          # Let the base class default method raise the TypeError
          return json.JSONEncoder.default(self, o)

#
# Define some exceptions.  Everybody should subclass PortalError.
#
class PortalError (Exception):
  def __init__(self,message):
    super(PortalError, self).__init__()
    self.message = message

  def __str__(self):
    return self.__class__.__name__ + ": " + self.message

  def __objdict__(self):
    retval = dict({ 'errorType': self.__class__.__name__, })
    for k in self.__dict__.keys():
      if k == 'errorType':
        continue
      if k.startswith('_'):
        continue
      retval[k] = self.__dict__[k]
    return retval


class ParameterError (PortalError):
  """
  A simple class to describe a parameter error.  If you need to report
  an error with a user-specified parameter value to the Portal UI,
  please create (don't throw) one of these error objects, and tell the
  Portal about it by calling Context.reportError.
  """
  def __init__(self,message,paramList):
    """
    Create a ParameterError.  @message is the overall error message;
    in the Portal Web UI, it will be displayed near each involved
    parameter for maximal impact.  @paramList is a list of the
    parameters that are involved in the error (often it is the
    combination of parameters that creates the error condition).
    The Portal UI will show this error message near *each* involved
    parameter to increase user understanding of the error.
    """
    super(ParameterError, self).__init__(message)
    self.params = paramList


class ParameterWarning (PortalError):
  """
  A simple class to describe a parameter warning.  If you need to
  report an warning with a user-specified parameter value to the
  Portal UI, please create (don't throw) one of these error objects,
  and tell the Portal about it by calling Context.reportWarning .  The
  first time the Portal UI runs your geni-lib script with a user's
  parameter values, it turns on the "warnings are fatal" mode (and
  then warnings are reported as errors).  This gives you a chance to
  warn the user that they might be about to do something stupid,
  and/or suggest a set of modified values that will improve the
  situation.  .
  """
  def __init__(self,message,paramList,fixedValues=None):
    """
    Create a ParameterWarning.  @message is the overall error
    message; in the Portal Web UI, it will be displayed near each
    involved parameter for maximal impact.  @paramList is a list of
    the parameters that are involved in the warning (often it is the
    combination of parameters that creates the error condition).
    The Portal UI will show this warning message near *each*
    involved parameter to increase user understanding of the error.
    If you supply the @fixedValue dict, the Portal UI will change
    the values the user submitted to those you suggest (and it will
    tell them it did so).  You might want to supply @fixedValues for
    a proper warning, because if something is only a warning, that
    implies your script can and will proceed in the absence of
    further user input.  But sometimes we want to let the user know
    that a parameter change will occur, so we warn them and
    autocorrect!
    """
    super(ParameterWarning, self).__init__(message)
    self.params = paramList
    if not fixedValues: fixedValues = {}
    self.fixedValues = fixedValues


class IllegalParameterDefaultError (PortalError):
  def __init__ (self,val):
    super(IllegalParameterDefaultError, self).__init__("no message?")
    self._val = val

  def __str__ (self):
    return "% given as a default value, but is not listed as a legal value" % self._val


class ParameterBindError (PortalError):
  def __init__ (self,val):
    super(ParameterBindError, self).__init__("no message?")
    self._val = val

  def __str__ (self):
    return "bad parameter binding: %s" % str(self._val,)


class NoRSpecError (PortalError):
  def __init__ (self,val):
    super(NoRSpecError, self).__init__("no message?")
    self._val = val

  def __str__ (self):
    return "No RSpec given: %s" % str(self._val,)

class MultipleRSpecError (PortalError):
  def __init__ (self,val):
    super(MultipleRSpecError, self).__init__("no message?")
    self._val = val

  def __str__ (self):
    return "Only one RSpec can be bound to a portal.Context"
