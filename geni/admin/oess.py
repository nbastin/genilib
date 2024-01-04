# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import requests.auth

from ..types import DPID


class Workgroup(object):
  def __init__ (self, name, workgroup_id):
    self.workgroup_id = int(workgroup_id)
    self.name = name

  def __repr__ (self):
    return "[%d] %s" % (self.workgroup_id, self.name)

class Node(object):
  def __init__ (self, ndata):
    self.dpid = DPID(long(ndata["dpid"]))
    self.name = ndata["name"]
    self.node_id = int(ndata["node_id"])
    self.state = ndata["operational_state"]
    self.send_barrier_bulk = bool(int(ndata["send_barrier_bulk"]))

  def __repr__ (self):
    return str(self.__dict__)

class Connection(object):
  BASE = "https://%s/oess/services/%s"

  def __init__ (self, hostname, uname, passwd):
    self.hostname = hostname
    self.url = Connection.BASE % (self.hostname, "data.cgi")
    self.purl = Connection.BASE % (self.hostname, "provisioning.cgi")
    self.auth = requests.auth.HTTPBasicAuth(uname, passwd)
    self.workgroup_id = None

  def setAuthInfo (self, uname, passwd):
    self.auth = requests.auth.HTTPBasicAuth(uname, passwd)

  @property
  def workgroups (self):
    r = requests.get(self.url, auth=self.auth, params={"action":"get_workgroups"})
    wgs = []
    for wg in r.json()["results"]:
      wgs.append(Workgroup(wg["name"], wg["workgroup_id"]))
    return wgs

  @property
  def nodes (self):
    r = requests.get(self.url, auth=self.auth, params={"action":"get_all_node_status"})
    nl = []
    for nd in r.json()["results"]:
      nl.append(Node(nd))
    return nl

  @property
  def circuits (self):
    r = requests.get(self.url, auth=self.auth, params={"action":"get_existing_circuits",
                                                       "workgroup_id":self.workgroup_id})
    return r.json()["results"]

  def getNodeInterfaces (self, name):
    r = requests.get(self.url, auth=self.auth,
                     params={"action":"get_node_interfaces", "workgroup_id":self.workgroup_id,
                             "node":name})
    return r.json()["results"]

  def provisionVLANPatch (self, desc, tag, node_name, intf_a_name, intf_b_name):
    payload = {"action" : "provision_circuit", "workgroup_id" : self.workgroup_id,
               "circuit_id" : -1, "description" : desc, "bandwidth" : 0, "provision_time": -1,
               "remove_time" : -1, "link" : [], "backup_link" : [], "remote_nodes" : [],
               "remote_tags" : [], "restore_to_primary" : 0, "node" : [], "interface" : [],
               "tag" : []}

    payload["node"].append(node_name)
    payload["interface"].append(intf_a_name)
    payload["tag"].append(tag)

    payload["node"].append(node_name)
    payload["interface"].append(intf_b_name)
    payload["tag"].append(tag)

    r = requests.post(self.purl, auth=self.auth, data = payload)
    return r.json()["results"]
