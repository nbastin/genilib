#!/usr/bin/env python
# Copyright (c) 2015-2017  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import os
import os.path
import code

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--debug", dest = "debug", action="store_true", default=False)
  parser.add_argument("--admin", dest="admin", action="store_true", default=False)
  parser.add_argument("--path", dest="path", default=None)
  return parser.parse_args()


class Shell(object):
  def __init__ (self, debug = False, admin = False, path = None):
    super(Shell, self).__init__()
    self.debug = debug
    self.admin = admin
    self.path = path

  def run (self, options):
    import geni._coreutil
    imports = geni._coreutil.shellImports()

    try:
      import readline
    except ImportError:
      pass
    else:
      import rlcompleter
      readline.set_completer(rlcompleter.Completer(imports).complete)
      readline.parse_and_bind("tab:complete")

    # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
    # conventions and get $PYTHONSTARTUP first then .pythonrc.py.
    for pythonrc in (os.environ.get("PYTHONSTARTUP"), '~/.pythonrc.py'):
      if not pythonrc:
        continue
      pythonrc = os.path.expanduser(pythonrc)
      if not os.path.isfile(pythonrc):
        continue
      try:
        with open(pythonrc) as handle:
          exec(compile(handle.read(), pythonrc, 'exec'), imports)
      except NameError:
        pass

    if self.debug:
      import geni.minigcf.chapi2
      import geni.minigcf.amapi2
      import geni.minigcf.pgch1
      import geni.minigcf.config
      imports["CH2"] = geni.minigcf.chapi2
      imports["AM2"] = geni.minigcf.amapi2
      imports["CFG"] = geni.minigcf.config
      imports["PG1"] = geni.minigcf.pgch1

    if self.admin:
      import geni.admin.vts
      imports["VTSADM"] = geni.admin.vts

    try:
      import getpass
      if self.path:
        passwd = getpass.getpass("Private key passphrase: ")
        imports["context"] = geni.util.loadContext(path = self.path, key_passphrase=passwd)
      elif geni.util.hasDataContext():
        passwd = getpass.getpass("Private key passphrase: ")
        imports["context"] = geni.util.loadContext(key_passphrase=passwd)
    except IOError:
      pass

    code.interact(banner="GENI-Lib Interactive Shell", local=imports)

def main():
  import sys
  sys.path.insert(0, os.path.realpath(os.path.curdir))

  opts = parse_args()

  s = Shell(opts.debug, opts.admin, opts.path)
  s.run(None)
