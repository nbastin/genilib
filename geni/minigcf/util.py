# Copyright (c) 2017-2020  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from six.moves import xmlrpc_client as xmlrpclib

import requests

from .. import _coreutil as GCU
from . import config

GCU.disableUrllibWarnings()

def headers ():
  return GCU.defaultHeaders()

# pylint: disable=unsubscriptable-object
def _rpcpost (url, req_data, cert, root_bundle):
  if isinstance(config.HTTP.LOG_URLS, tuple):
    config.HTTP.LOG_URLS[0].log(config.HTTP.LOG_URLS[1], "POST: %s" % (url))
  s = requests.Session()
  s.mount(url, GCU.TLSHttpAdapter())
  if isinstance(config.HTTP.LOG_RAW_REQUESTS, tuple):
    config.HTTP.LOG_RAW_REQUESTS[0].log(config.HTTP.LOG_RAW_REQUESTS[1], req_data)
  resp = s.post(url, req_data, cert=cert, verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if resp.status_code != 200:
    resp.raise_for_status()
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content, use_datetime=True)[0][0]
