# Copyright (c) 2015-2018  Barnstormer Softworks, Ltd.
# Copyright (c) 2020  University of Houston Networking Lab

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# genish as an iPython extension for use with Jupyter

from __future__ import print_function

import copy
import itertools
import os.path
import types

import graphviz
import six
import wrapt

from geni.aggregate.exceptions import AMError
from geni.aggregate.frameworks import KeyDecryptionError
from geni.aggregate.vts import VTS, HostPOAs, v4RouterPOAs
import geni.rspec.vtsmanifest
import geni.util
import geni.types

SHOW_ERROR_URL = False

######
### iPython-specific Utilities
######

def am_exc_handler (self, etype, value, tb, tb_offset = None):
  # The ipython docs for this handler are a lie - returning a structured traceback
  # is useless (ipython burns CPU cycles validating it, but never actually displays
  # any of it), you need to take care of all display yourself

  Colors = self.InteractiveTB.Colors


  out = []
  out.append("%s%s:%s %s" % (Colors.excName, etype.__name__, Colors.Normal, str(value)))

  if SHOW_ERROR_URL:
    try:
      out.append("AM Log URL: <%s>" % (value.error_url))
    except AttributeError:
      pass
  print("\n".join(out))


def topo (manifests, engine = "circo"):
  if not isinstance(manifests, list):
    manifests = [manifests]

  dotstr = geni.util.builddot(manifests)
  g = graphviz.Source(dotstr)
  g.engine = engine
  return g

LOGINROW = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>"
LOGINCOLS = ["Client-ID", "Username", "Host", "Port"]


def loginInfo (manifests):
  linfo = geni.util._corelogininfo(manifests)
  return RetListProxy(linfo, LOGINCOLS, LOGINROW, tupl = True)

def showErrorURL (show = False):
  global SHOW_ERROR_URL # pylint disable=global-statement
  SHOW_ERROR_URL = show


gsh = types.ModuleType("geni_ipython_util")
setattr(gsh, "showtopo", topo)
setattr(gsh, "printlogininfo", loginInfo)
setattr(gsh, "showErrorURL", showErrorURL)

#####
### Converters
#####

# Not actually supported right now, my brain doesn't want to figure it out
class Direction(object):
  TTB = 0
  LTR = 1

class ListGrid(object):
  def __init__ (self, iterable, cols, hdr, sort):
    self.iterable = iterable
    self.cols = cols
    self.header = ""
    self.sort = sort
    if hdr:
      self.header = """<tr><th colspan="%d" scope="row"><b>%s</b></th></tr>""" % (cols, hdr)
    rowc = ["<tr>"]
    for idx in range(cols):
      rowc.append("<td>%s</td>")
    rowc.append("</tr>")
    self.row = "".join(rowc)

  def _repr_html_ (self):
    if self.sort:
      contents = sorted([x for x in self.iterable])
      args = [iter(contents)] * self.cols
    else:
      args = [iter(self.iterable)] * self.cols
    rows = [self.row % tuple([str(y) for y in x]) for x in itertools.izip_longest(fillvalue="&nbsp;", *args)]
    out = """
    <table>
    %s
    %s
    </table>
    """ % (self.header, "\n".join(rows))
    return out

def listGridMaker (iterable, cols = 2, hdr = None, sort = False):
  return ListGrid(iterable, cols, hdr, sort)

setattr(gsh, "grid", listGridMaker)


STP_PORT_ROW = """<tr>
<td>%(client-id)s (%(num)d)</td><td>%(stp_state)s</td><td>%(stp_role)s</td><td>%(stp_port_id)s</td><td>%(stp_sec_in_state)s</td>
<td>%(stp_rx_count)d</td><td>%(stp_tx_count)d</td><td>%(stp_error_count)d</td>
</tr>"""

class STPProxy(wrapt.ObjectProxy):
  def _repr_html_ (self):
    brt = """
  <table>
    <tr><th colspan="3" scope="row">Bridge: <b>%(client-id)s</b></th></tr>
    <tr><th>Bridge ID</th><th>Designated Root</th><th>Root Path Cost</th></tr>
    <tr><td>%(stp_bridge_id)s</td><td>%(stp_designated_root)s</td><td>%(stp_root_path_cost)s</td></tr>
  </table>""" % (self)
    pelist = []
    for port in self["ports"]:
      d = {}
      d.update(port)
      d.update(port["info"])
      pe = STP_PORT_ROW % (d)
      pelist.append(pe)
    pt = """
  <table>
    <tr><th>Port</th><th>State</th><th>Role</th><th>Port ID</th><th>In State (secs)</th><th>RX</th><th>TX</th><th>Errors</th></tr>
    %s
  </table>
  """ % ("\n".join(pelist))
    return "%s\n%s" % (brt,pt)


RSTP_PORT_ROW = """<tr>
<td>%(client-id)s (%(num)d)</td><td>%(rstp_port_state)s</td><td>%(rstp_port_role)s</td><td>%(rstp_port_id)s</td>
<td>%(rstp_uptime)s</td><td>%(rstp_rx_count)d</td><td>%(rstp_tx_count)d</td><td>%(rstp_error_count)d</td>
</tr>"""

class RSTPProxy(wrapt.ObjectProxy):
  def _repr_html_ (self):
    brt = """
  <table>
    <tr><th colspan="3" scope="row">Bridge: <b>%(client-id)s</b></th></tr>
    <tr><th>Bridge ID</th><th>Designated Root</th><th>Root Path Cost</th></tr>
    <tr><td>%(rstp_bridge_id)s</td><td>%(rstp_root_id)s</td><td>%(rstp_root_path_cost)s</td></tr>
  </table>""" % (self)
    pelist = []
    for port in self["ports"]:
      d = {}
      d.update(port)
      d.update(port["info"])
      pe = RSTP_PORT_ROW % (d)
      pelist.append(pe)
    pt = """
  <table>
    <tr><th>Port</th><th>State</th><th>Role</th><th>Port ID</th><th>Uptime (secs)</th><th>RX</th><th>TX</th><th>Errors</th></tr>
    %s
  </table>
  """ % ("\n".join(pelist))
    return "%s\n%s" % (brt,pt)


def dictListBuilder (objlist, filter_cols, display_names):
  flist = []
  for obj in objlist:
    newl = []
    for col in filter_cols:
      newl.append(obj[col])
    flist.append(newl)

  rtemplate = "<tr>%s</tr>" % ("".join(["<td>{%d}</td>" % (x) for x in range(len(display_names))]))

  return RetListProxy(flist, display_names, rtemplate, True)


class RetListProxy(object):
  def __init__ (self, obj, columns, row_template, tupl = False):
    self._obj = obj
    self._columns = columns
    self._row_template = row_template
    self._col_template = "<th>%s</th>"
    self._tuple = tupl

  def __len__ (self):
    return len(self._obj)

  def __getitem__ (self, i):
    return self._obj[i]

  def __getslice__ (self, i, j):
    i = max(i, 0)
    j = max(j, 0)
    return self._obj[i:j]

  def __contains__ (self, item):
    return item in self._obj

  def __iter__ (self):
    for x in self._obj:
      yield x

  def _repr_html_ (self):
    trlist = []
    for row in self._obj:
      if self._tuple:
        trlist.append(self._row_template.format(*row))
      else:
        trlist.append(self._row_template.format(**row))

    collist = []
    for column in self._columns:
      collist.append(self._col_template % (column))

    return """<table>\n<tr>%s</tr>\n%s\n<table""" % ("".join(collist), "\n".join(trlist))
      

LEASEROW = "<tr><td>{hostname}</td><td>{ip-address}</td><td>{mac-address}</td><td>{binding-state}</td><td>{end:%Y-%m-%d %H:%M:%S}</td></tr>"
LEASECOLS = ["Hostname", "IP Address", "MAC Address", "State", "End"]

PINFOCOLS = ["Client ID", "ifindex", "vlan", "MTU", "Admin State", "Link State", "RX Bytes (Pkts)", "TX Bytes (Pkts)"]
PINFOROW = "<tr><td>{client-id}</td><td>{ifindex}</td><td>{tag}</td><td>{mtu}</td><td>{admin_state}</td><td>{link_state}</td><td>{statistics[rx_bytes]} ({statistics[rx_packets]})</td><td>{statistics[tx_bytes]} ({statistics[tx_packets]})</td></tr>"

FLOWCOLS = ["Table", "Duration", "Packets", "Bytes", "Rule"]
FLOWROW = "<tr><td>{table_id}</td><td>{duration}</td><td>{n_packets}</td><td>{n_bytes}</td><td>{rule}</td></tr>"

MACCOLS = ["Port", "VLAN", "MAC", "Age"]
MACROW = "<tr><td>{port}</td><td>{vlan}</td><td>{mac}</td><td>{age}</td></tr>"

#####
### Core geni-lib monkeypatches
#####

def replaceSymbol (module, name, func):
  """Moves module.name to module._name and sets module.name to the new function object."""
  setattr(module, "_%s" % (name), getattr(module, name))
  setattr(module, name, func)

def macTableDecomp (table):
  rowobjs = []
  for row in table[1:]:
    d = {}
    d["port"] = row[0]
    d["vlan"] = row[1]
    d["mac"] = geni.types.EthernetMAC(row[2])
    if row[3] is None:
      d["age"] = "-"
    else:
      d["age"] = int(row[3])
    rowobjs.append(d)
  return rowobjs

def flowTableDecomp (table):
  TEMPLATE = {"table_id" : 0, "duration" : None, "n_packets" : 0, "n_bytes" : None}
  rows = [[y.strip(",") for y in x.split(" ")] for x in table]
  rmaps = []
  for row in rows:
    rmap = copy.copy(TEMPLATE)
    for item in row[:-1]:
      (key,val) = item.split("=")
      rmap[key] = val
    rmap["rule"] = row[-1]
    rmaps.append(rmap)
  return rmaps

def dumpFlows (self, context, sname, datapaths, **kwargs):
  if not isinstance(datapaths, list):
    datapaths = [datapaths]

  res = self._dumpFlows(context, sname, datapaths, **kwargs)

  if len(res) == 1:
    values = list(res.values())
    return RetListProxy(flowTableDecomp(values[0]), FLOWCOLS, FLOWROW)

  retd = {}
  for brname,table in res.items():
    retd[brname] = RetListProxy(flowTableDecomp(table), FLOWCOLS, FLOWROW)
  return retd

def getSTPInfo (self, context, sname, datapaths):
  if not isinstance(datapaths, list):
    datapaths = [datapaths]

  res = self._getSTPInfo(context, sname, datapaths)
  if len(res) == 1:
    return STPProxy(res[0])

  retobj = {}
  for br in res:
    retobj[br["client-id"]] = STPProxy(br)
  return retobj

def getRSTPInfo (self, context, sname, datapaths):
  if not isinstance(datapaths, list):
    datapaths = [datapaths]

  res = self._getRSTPInfo(context, sname, datapaths)
  if len(res) == 1:
    return RSTPProxy(res[0])

  retobj = {}
  for br in res:
    retobj[br["client-id"]] = RSTPProxy(br)
  return retobj


def getLeaseInfo (self, context, sname, client_ids):
  if not isinstance(client_ids, list):
    client_ids = [client_ids]

  res = self._getLeaseInfo(context, sname, client_ids)
  
  if len(res) == 1:
    values = list(res.values())
    return RetListProxy(values[0], LEASECOLS, LEASEROW)
  
  retobj = {}
  for k,v in res.items():
    retobj[k] = RetListProxy(v, LEASECOLS, LEASEROW)
  return retobj

def getPortInfo (self, context, sname, client_ids):
  res = self._getPortInfo(context, sname, client_ids)

  if len(res) == 1:
    values = list(res.values())
    return RetListProxy(values[0], PINFOCOLS, PINFOROW)

  retobj = {}
  for k,v in res.items():
    retobj[k] = RetListProxy(v, PINFOCOLS, PINFOROW)
  return retobj

def portDown (self, context, sname, port):
  if isinstance(port, (six.text_type)):
    pass
  elif isinstance(port, geni.rspec.vtsmanifest.GenericPort):
    port = port.client_id

  return self._portDown(context, sname, port)

def portUp (self, context, sname, port):                                                                                     
  if isinstance(port, (six.text_type)):                                                                                         
    pass
  elif isinstance(port, geni.rspec.vtsmanifest.GenericPort):                                                                   
    port = port.client_id                                                                                                      
              
  return self._portUp(context, sname, port)     

replaceSymbol(VTS, "dumpFlows", dumpFlows)
replaceSymbol(VTS, "getSTPInfo", getSTPInfo)
replaceSymbol(VTS, "getRSTPInfo", getRSTPInfo)
replaceSymbol(VTS, "getLeaseInfo", getLeaseInfo)
replaceSymbol(VTS, "getPortInfo", getPortInfo)
replaceSymbol(VTS, "portDown", portDown)
replaceSymbol(VTS, "portUp", portUp)


def getL2Table (self, context, sname, client_ids):
  if not isinstance(client_ids, list):
    client_ids = [client_ids]

  res = self._getL2Table(context, sname, client_ids)

  if len(res) == 1:
    values = list(res.values())
    return RetListProxy(macTableDecomp(values[0]), MACCOLS, MACROW)

  retd = {}
  for l2d in res:
    for bridge, table in l2d.items():
      rowobjs = macTableDecomp(table)
      retd[bridge] = RetListProxy(rowobjs, MACCOLS, MACROW)

  return retd

def clearL2Table (self, context, sname, client_ids):
  if not isinstance(client_ids, list):
    client_ids = [client_ids]

  res = self._clearL2Table(context, sname, client_ids)

  return res

replaceSymbol(VTS, "getL2Table", getL2Table)
replaceSymbol(VTS, "clearL2Table", clearL2Table)


ARP_FILTER = ["hw-address", "ip-address", "status", "device"]
ARP_COLS = ["HW Address", "IP Address", "Status", "Interface"]
def getARPTable (self, context, sname, client_ids):
  res = self._getARPTable(context, sname, client_ids)

  if len(res.items()) == 1:
    return dictListBuilder(res.popitem()[1], ARP_FILTER, ARP_COLS)

  retobj = {}
  for k,v in res.items():
    retobj[k] = dictListBuilder(v, ARP_FILTER, ARP_COLS)
  return retobj
replaceSymbol(HostPOAs, "getARPTable", getARPTable)

ROUTE_FILTER = ["destination", "mask", "gateway", "device"]
ROUTE_COLS = ["Destination", "Mask", "Gateway", "Interface"]
def getRouteTable (self, context, sname, client_ids):
  res = self._getRouteTable(context, sname, client_ids)

  if len(res.items()) == 1:
    return dictListBuilder(res.popitem()[1], ROUTE_FILTER, ROUTE_COLS)

  retobj = {}
  for k,v in res.items():
    retobj[k] = dictListBuilder(v, ROUTE_FILTER, ROUTE_COLS)
  return retobj
replaceSymbol(HostPOAs, "getRouteTable", getRouteTable)

QROUTE_FILTER = ["type", "selected", "network", "next-hop", "interface", "time"]
QROUTE_COLS = ["", "Selected", "Network", "Next Hop", "Interface", "Duration"]
def getIPRouteTable (self, context, sname, client_ids):
  res = self._getRouteTable(context, sname, client_ids)
  if len(res.items()) == 1:
    return dictListBuilder(res.popitem()[1], QROUTE_FILTER, QROUTE_COLS)

  retobj = {}
  for k,v in res.items():
    retobj[k] = dictListBuilder(v, QROUTE_FILTER, QROUTE_COLS)
  return retobj
replaceSymbol(v4RouterPOAs, "getRouteTable", getIPRouteTable)

NEIGHBOR_FILTER = ["id", "priority", "state", "dead-time", "address", "interface"]
NEIGHBOR_COLS = ["ID", "Priority", "State", "Dead Time", "Address", "Interface"]
def getOSPFNeighbors (self, context, sname, client_ids):
  res = self._getOSPFNeighbors(context, sname, client_ids)
  if len(res.items()) == 1:
    return dictListBuilder(res.popitem()[1], NEIGHBOR_FILTER, NEIGHBOR_COLS)

  retobj = {}
  for k,v in res.items():
    retobj[k] = dictListBuilder(v, NEIGHBOR_FILTER, NEIGHBOR_COLS)
  return retobj
replaceSymbol(v4RouterPOAs, "getOSPFNeighbors", getOSPFNeighbors)

DNSRR_FILTER = ["type", "name", "value"]
DNSRR_COLS = ["Type", "Name", "Value"]
def getAllDNSResourceRecords(self, context, sname, client_ids):
  res = self._getAllDNSResourceRecords(context, sname, client_ids)
  if len(res.items()) == 1:
    return dictListBuilder(res.popitem()[1], DNSRR_FILTER, DNSRR_COLS)

  retobj = {}
  for k,v in res.items():
    retobj[k] = dictListBuilder(v, DNSRR_FILTER, DNSRR_COLS)
  return retobj
replaceSymbol(VTS, "getAllDNSResourceRecords", getAllDNSResourceRecords)

LASTDNSDHC_FILTER = ["data"]
LASTDNSDHC_COLS = ["Log"]
def getLastDNSDHCPops(self, context, sname, client_ids, count, type):
  res = self._getLastDNSDHCPops(context, sname, client_ids, count, type)
  if len(res.items()) == 1:
    return dictListBuilder(res.popitem()[1], LASTDNSDHC_FILTER, LASTDNSDHC_COLS)

  retobj = {}
  for k,v in res.items():
    retobj[k] = dictListBuilder(v, LASTDNSDHC_FILTER, LASTDNSDHC_COLS)
  return retobj
replaceSymbol(VTS, "getLastDNSDHCPops", getLastDNSDHCPops)

class NoContextError(Exception):
  def __str__ (self):
    return "No context found, extension cannot be loaded."

#####
### Extension loader
#####
def load_ipython_extension (ipy):
  import geni.util

  if not geni.util.hasDataContext():
    path = os.path.expanduser("~/omni.bundle")
    if os.path.exists(path):
      geni.util.buildContextFromBundle(path, pubkey_path = geni.util.MAKE_KEYPAIR)

  if not geni.util.hasDataContext():
    raise NoContextError()

  import geni._coreutil
  imports = geni._coreutil.shellImports()
  imports["genish"] = gsh

  import getpass

  tries = 0
  need_pw = False

  try:
    context = geni.util.loadContext(key_passphrase = "ffffffffff")
  except TypeError:
    context = geni.util.loadContext()
  except KeyDecryptionError:
    need_pw = True

  if need_pw:
    while True:
      pw = getpass.getpass("Private Key Passphrase: ")
      tries += 1
      try:
        imports["context"] = geni.util.loadContext(key_passphrase = pw)
        break
      except KeyDecryptionError:
        if tries < 3:
          continue
        break
      except IOError:
        break
  else:
    imports["context"] = context

  ipy.push(imports)
  ipy.set_custom_exc((AMError,), am_exc_handler)
