#!/usr/bin/env python
# Copyright (c) 2015-2016  Barnstormer Softworks, Ltd.

import argparse
import json
import os
import os.path
import sys
import zipfile

import geni._coreutil as GCU
import geni.util

def parse_args ():
  parser = argparse.ArgumentParser()
  parser.add_argument("--pubkey", dest="pubkey_path", help="Path to public key file", default = None)
  parser.add_argument("--bundle", dest="bundle_path", help="Path to omni.bundle", default="omni.bundle")
  parser.add_argument("--cert-private-key", dest="cert_pkey_path", help="Path to certificate private key file", default=None)
  return parser.parse_args()

def main():
  opts = parse_args()
  geni.util.buildContextFromBundle(opts.bundle_path, opts.pubkey_path, opts.cert_pkey_path)
