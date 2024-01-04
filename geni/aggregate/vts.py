# Copyright (c) 2014-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import sys
import inspect

from .core import AM, APIRegistry

class HostPOAs(object):
  def __init__ (self, vtsam):
    self.am = vtsam

  def getARPTable (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self.am._apiv3.poa(context, self.am.urlv3, sname, "api:uh.host:get-arp-table",
                              options={"client-ids": client_ids})

  def getRouteTable (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self.am._apiv3.poa(context, self.am.urlv3, sname, "api:uh.host:get-route-table",
                              options={"client-ids": client_ids})

  def svcStatus (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self.am._apiv3.poa(context, self.am.urlv3, sname, "api:uh.host:supervisor-status",
                              options={"client-ids": client_ids})

  def execcmd (self, context, sname, client_ids, cmd):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self.am._apiv3.poa(context, self.am.urlv3, sname, "api:uh.host:exec",
                              options={"client-ids": client_ids, "cmd" : cmd})


class v4RouterPOAs(object):
  def __init__ (self, vtsam):
    self.am = vtsam

  def addOSPFNetworks (self, context, sname, client_ids, nets):
    """Add OSPF Networks to areas on the given routers

    Args:
      context: geni-lib context
      sname (str): Slice name
      client_ids (list): A list of client-id strings
      nets (list): A list of (network, area) tuples
    """
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self.am._apiv3.poa(context, self.am.urlv3, sname, "vts:uh.quagga:add-ospf-nets",
                              options={"client-ids": client_ids, "networks" : nets})

  def getRouteTable (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self.am._apiv3.poa(context, self.am.urlv3, sname, "vts:uh.quagga:get-route-table",
                              options={"client-ids": client_ids})

  def getOSPFNeighbors (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self.am._apiv3.poa(context, self.am.urlv3, sname, "vts:uh.quagga:get-ospf-neighbors",
                              options={"client-ids": client_ids})


class Policy(object):
  def __init__ (self, vtsam):
    self.am = vtsam

  # Policy consent hooks for GDPR-style compliance
  def getText (self, context, pid = None):
    """Get the text contents of the policy requested.  If no policy is specified and only one policy
    exists at the aggregate, that policy text will be returned.

    Args:
      context: geni-lib context
      pid: policy ID (typically from `getversion` output)

    Returns:
      str: Text contents of policy
    """
    opts = {}
    if pid:
      opts["policy-id"] = pid
    return self.am._apiv3.paa(context, self.am.urlv3, "vts:policy:get-text", options = opts)

  def giveConsent (self, context, pid):
    """Give consent to the policy indicated for the user URN in the credential used.

    Args:
      context: geni-lib context
      pid: policy ID
    """
    return self.am._apiv3.paa(context, self.am.urlv3, "vts:policy:consent", options = {"policy-id" : pid})

  def revokeConsent (self, context, pid):
    """Revoke consent from this date forward to the policy indicated for the user URN in the credential used.

    Args:
      context: geni-lib context
      pid: policy ID
    """
    return self.am._apiv3.paa(context, self.am.urlv3, "vts:policy:revoke", options = {"policy-id" : pid})


class VTS(AM):
  """Wrapper for all VTS-supported AMAPI functions"""

  def __init__ (self, name, host, url = None):
    self._host = host
    if url is None:
      url = "https://%s:3626/foam/gapi/2" % (self._host)
    self.urlv3 = "%s3" % (url[:-1])
    self._apiv3 = APIRegistry.get("amapiv3")
    super(VTS, self).__init__(name, url, "amapiv2", "vts")
    self.Host = HostPOAs(self)
    self.IPv4Router = v4RouterPOAs(self)
    self.Policy = Policy(self)

  def allocate (self, context, sname, rspec):
    rspec_data = rspec.toXMLString(ucode=True)
    manifest = self._apiv3.allocate(context, self.urlv3, sname, rspec_data)
    return self.amtype.parseManifest(manifest)

  def provision (self, context, sname):
    udata = []
    for user in context._users:
      data = {"urn" : user.urn, "keys" : [open(x, "rb").read() for x in user._keys]}
      udata.append(data)

    res = self._apiv3.provision(context, self.urlv3, sname, options = {"geni_users" : udata})
    if res["code"]["geni_code"] == 0:
      return self.amtype.parseManifest(res["value"])

  def changeController (self, context, sname, url, datapaths, ofver=None):
    options={"controller-url" : url, "datapaths" : datapaths}
    if ofver:
      options["openflow-version"] = ofver
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:change-controller", options)

  def dumpFlows (self, context, sname, datapaths, show_hidden=False):
    """Get the current flows and flow stats from the requested datapaths.
    
    Args:
      context: geni-lib context
      sname (str): Slice name
      datapaths (list): A list of datapath client_id strings
      show_hidden (bool): Show hidden flows (if any)

    Returns:
      dict: Key/Value dictionary of format `{ client_id : [(flow_field, ...), ...] }`
    """
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:dump-flows",
                           options={"datapaths" : datapaths, "show-hidden" : show_hidden})

  def getL2Table (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self._apiv3.poa(context, self.urlv3, sname, "api:l2-switch:get-l2-table",
                           options={"client-ids" : client_ids})

  def clearL2Table (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self._apiv3.poa(context, self.urlv3, sname, "api:uh.vswitch:clear-l2-table",
                           options={"client-ids" : client_ids})

  def clearFlows (self, context, sname, datapaths):
    """Clear all installed flows from the requested datapaths.

    Args:
      context: geni-lib context
      sname (str): Slice name
      datapaths (list): A list of datapath client_id strings
    """
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:clear-flows", options={"datapaths" : datapaths})

  def portDown (self, context, sname, client_id):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:port-down",
                           options={"port-client-id" : client_id})

  def portUp (self, context, sname, client_id):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:port-up",
                           options={"port-client-id" : client_id})

  def addFlows (self, context, sname, flows):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:add-flows", options={"rules" : flows})

  def getSTPInfo (self, context, sname, datapaths):
    if not isinstance(datapaths, list): datapaths = [datapaths]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:l2:stp-info",
                           options={"datapaths" : datapaths})

  def getRSTPInfo (self, context, sname, datapaths):
    if not isinstance(datapaths, list): datapaths = [datapaths]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:l2:rstp-info",
                           options={"datapaths" : datapaths})

  def getPortInfo (self, context, sname, datapaths):
    if not isinstance(datapaths, list): datapaths = [datapaths]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:raw:get-port-info",
                           options={"datapaths" : datapaths})

  def setPortBehaviour (self, context, sname, port_list):
    port_json_list = []
    for (port,obj) in port_list:
      port_json_list.append((port, obj.__json__()))
    return self._apiv3.poa(context, self.urlv3, sname, "vts:raw:set-port-behaviour",
                           options={"ports" : port_json_list})

  def getLeaseInfo (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self._apiv3.poa(context, self.urlv3, sname, "api:uh.dhcp:get-leases",
                           options = {"client-ids" : client_ids})

  def setPortVLAN (self, context, sname, port_tuples):
    if not isinstance(port_tuples, list): port_tuples = [port_tuples]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:raw:set-vlan",
                           options = {"ports" : port_tuples})

  def setPortTrunk (self, context, sname, port_list):
    if not isinstance(port_list, list): port_list = [port_list]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:raw:set-trunk",
                           options = {"ports" : port_list})

  def addSSHKeys (self, context, sname, client_ids, keys):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    if not isinstance(keys, list): keys = [keys]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:container:add-keys",
                           options = {"client-ids" : client_ids, "ssh-keys" : keys})

  def setDHCPSubnet (self, context, sname, subnet_tuples):
    if not isinstance(subnet_tuples, list): subnet_tuples = [subnet_tuples]
    clid_map = {}
    for clid,subnet in subnet_tuples:
      clid_map[clid] = subnet

    return self._apiv3.poa(context, self.urlv3, sname, "api:uh.dhcp:set-subnet",
                         options = {"client-id-map" : clid_map})



  def addDNSResourceRecord (self, context, sname, client_id, record_name, record_type, record_value, record_ttl=7200):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:uh.dnsroot:add-resource-record",
                           options = {"client-id" : client_id,
                           "record-name" : record_name,
                           "record-type" : record_type,
                           "record-value" : record_value,
                           "record-ttl" : record_ttl})

  def deleteDNSResourceRecord (self, context, sname, client_id, record_name, record_type):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:uh.dnsroot:delete-resource-record",
                           options = {"client-id" : client_id,
                           "record-name" : record_name,
                           "record-type" : record_type})

  def getAllDNSResourceRecords(self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:uh.dnsroot:get-all-records",
                           options={"client-ids": client_ids})

  def getLastDNSDHCPops(self, context, sname, client_ids, number_of_operations, dns_OR_dhcp):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:uh.dnsdhcp:get-last-DNSDHCP-ops",
                           options={"client-ids": client_ids,
                           "number-of-operations": number_of_operations,
                           "dns-OR-dhcp": dns_OR_dhcp})


  def setDeleteLock (self, context, sname):
    """Prevent the given sliver from being deleted by another user with the credential.

    .. note::
      Locks are cumulative, and removed by calling `deletesliver`.  When the last locking
      user calls `deletesliver`, the sliver will be deleted.  It is not possible to remove
      your lock without risking deletion.

    Args:
      context: geni-lib context
      sname (str): Slice name
    """
    return self._apiv3.poa(context, self.urlv3, sname, "geni:set-delete-lock", {})

  def dropboxLink (self, context):
    """Link your user_urn to a Dropbox account at this aggregate.

    Args:
      context: geni-lib context

    Returns:
      str: Dropbox authorization URL to paste into web browser
    """
    return self._apiv3.paa(context, self.urlv3, "vts:dropbox:link-account")

  def dropboxFinalize (self, context, authcode):
    """Finalize the Dropbox account link for this aggregate.

    Args:
      context: geni-lib context
      authcode (str): Authorization code given by Dropbox
    """
    return self._apiv3.paa(context, self.urlv3, "vts:dropbox:complete-link", {"auth-code" : authcode})

  def dropboxUpload (self, context, sname, cvols):
    """Trigger upload to associated Dropbox account from requested container volumes.

    Args:
      context: geni-lib context
      sname (str): Slice name
      cvols (list): List of `(container client-id, volume-id)` tuples
    """
    data = {}
    for (cid,volid) in cvols:
      data.setdefault(cid, []).append(volid)
    return self._apiv3.poa(context, self.urlv3, sname, "vts:dropbox:upload", options = {"vols" : [data]})

  def hgPull (self, context, sname, cvols):
    """Update an HgMount volume with the latest data from the source repository.

    Args:
      context: geni-lib context
      sname (str): Slice name
      cvols (list): List of `(container client-id, volume-id)` tuples
    """

    data = {}
    for (cid,volid) in cvols:
      data.setdefault(cid, []).append((volid, True))
    return self._apiv3.poa(context, self.urlv3, sname, "vts:hg:pull", options = {"vols" : [data]})


Clemson = VTS("vts-clemson", "clemson.vts.bsswks.net")
GPO = VTS("vts-gpo", "gpo.vts.bsswks.net")
Illinois = VTS("vts-illinois", "uiuc.vts.bsswks.net")
NPS = VTS("vts-nps", "nps.vts.bsswks.net")
UKYPKS2 = VTS("vts-ukypks2", "ukypks2.vts.bsswks.net")
StarLight = VTS("vts-starlight", "starlight.vts.bsswks.net")


def aggregates ():
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj

def name_to_aggregate ():
  result = dict()
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      result[obj.name] = obj
  return result

def aggregateFromHost (host):
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      if obj._host == host:
        return obj
