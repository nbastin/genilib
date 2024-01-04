#!/usr/bin/env python

import geni.portal as portal
import geni.rspec.pg as PG
import geni.rspec.igext as IG
import geni.rspec.emulab.pnext as PN

#
# Global variables that should remain relatively static
#
class GLOBALS(object):
    EPCIMG = PN.PNDEFS.DEF_BINOEPC_IMG
    VM_COLLOCATE_FACTOR = 10  # Number of VMs to pack onto a phys node.

#
# Create our in-memory model of the RSpec -- the resources we're going
# to request in our experiment, and their configuration.
#
rspec = PG.Request()

#
# This geni-lib script is designed to run in the PhantomNet Portal.
#
pc = portal.Context()

#
# Describe profile.  Will be rendered in Markdown on Portal.
#
tourDescription = \
"""
###*<center>Use this profile to instantiate a basic EPC topology.</center>*
---
The following functions are included:

 * AAA
 * HSS
 * MME
 * SGW
 * PGW
 * eNodeB
 * UE

OpenEPC Release 5 software running on top of Ubuntu 12.04 LTS is used to implement this functionality. Please note that the disk image used does not allow root access, and only the OpenEPC binaries are present. Circumventing root restrictions and/or copying the OpenEPC binaries is prohibited.  Such actions constitute a violation of the PhantomNet/OpenEPC sublicense agreement.
"""

tourInstructions = \
"""
This profile makes use of user-supplied parameters. You can use these parameters to tune the number of clients (emulated UEs), request additional emulated eNodeBs, and to choose the hardware used.  An advanced parameter allows you to set the default LAN bandwidth.

This is a parameterized profile implemented via a [geni-lib](http://geni-lib.readthedocs.org "geni-lib documentation") script. You may make a copy of the script to use in your own profile where you can modify the script to suit your needs.
"""

#
# Setup the Tour info with the above description and instructions.
#  
tour = IG.Tour()
tour.Description(IG.Tour.MARKDOWN,tourDescription)
tour.Instructions(IG.Tour.MARKDOWN,tourInstructions)
rspec.addTour(tour)

#
# Define some parameters for OpenEPC experiments.
#
pc.defineParameter("NUMCLI", "Number of clients (UEs)",
                   portal.ParameterType.INTEGER, 1,
                   longDescription="Specify the number of emulated client (User Equipment) resources to allocate. This number must be between 1 and 32 currently.")

pc.defineParameter("NUMENB", "Number of eNodeB nodes.",
                   portal.ParameterType.INTEGER, 1,
                   [1,2,3],
                   longDescription="Number of emulated eNodeB (LTE base station) nodes to allocate.  May be from 1 to 3 (inclusive).")

pc.defineParameter("HWTYPE","Node Hardware Type",
                   portal.ParameterType.STRING, "pcvm",
                   [("pc","Any available (compatible) physical machine type"),
                    ("pc3000","Emulab pc3000 nodes"),
                    ("d710","Emulab d710 nodes"),
                    ("d430","Emulab d430 nodes"),
                    ("pcvm","Any available (compatible) virtual machine type"),
                    ("pc3000vm","Virtual machines on top of pc3000 nodes."),
                    ("d710vm","Virtual machines on top of d710 nodes."),
                    ("d430vm","Virtual machines on top of d430 nodes.")],
                   longDescription="Specify which node resource type to use for OpenEPC nodes. Note that only those types that are compatible with the OpenEPC image(s) are listed.")

pc.defineParameter("LINKBW","Default Link Bandwidth (Mbps)",
                   portal.ParameterType.INTEGER, 0,
                   longDescription="Specify the default LAN bandwidth in Mbps for all EPC LANs. Leave at \"0\" to indicate \"best effort\". Values that do not line up with common physical interface speeds (e.g. 10, 100, or 1000) WILL cause the insertion of link shaping elements.",
                   advanced=True)

#
# Get any input parameter values that will override our defaults.
#
params = pc.bindParameters()

#
# Verify parameters and setup errors/warnings to be reported back.
#
if params.NUMCLI > 32 or params.NUMCLI < 1:
    perr = portal.ParameterError("You cannot ask for fewer than one or more than 32 client nodes!", ['NUMCLI'])
    pc.reportError(perr)

if params.NUMENB < 1 or params.NUMENB > 3:
    perr = portal.ParameterError("You cannot ask for fewer than one or more than three eNodeB nodes!", ['NUMENB'])
    pc.reportError(perr)

if int(params.LINKBW) not in [0, 10, 100, 1000]:
    pwarn = portal.ParameterWarning("You are asking for a default link bandwidth that is NOT a standard physical link speed. Link shaping resources WILL be inserted!", ['LINKBW'])
    pc.reportWarning(pwarn)

#
# Give the library a chance to return nice JSON-formatted exception(s) and/or
# warnings; this might sys.exit().
#
pc.verifyParameters()

#
# Scale link bandwidth parameter to kbps
#
params.LINKBW *= 1000

#
# Switch up some settings if VMs were requested.
#
usevms = False
if params.HWTYPE.find("vm") >= 0:
    usevms = True
    PN.EPCNodeFactorySettings.use_vm_nodes = True
    params.HWTYPE = params.HWTYPE.replace("vm","")
    rspec.setCollocateFactor(GLOBALS.VM_COLLOCATE_FACTOR)
    rspec.setPackingStrategy("pack")

#
# Set the hardware and image for the epc node factory function
#
PN.EPCNodeFactorySettings.hardware_type = params.HWTYPE
PN.EPCNodeFactorySettings.disk_image = GLOBALS.EPCIMG

#
# Create the lans we need
#
mgmt = rspec.EPClan(PN.EPCLANS.MGMT, vmlan = usevms)
net_a = rspec.EPClan(PN.EPCLANS.NET_A, vmlan = usevms)
net_a.bandwidth = params.LINKBW
net_b = rspec.EPClan(PN.EPCLANS.NET_B, vmlan = usevms)
net_b.bandwidth = params.LINKBW
net_d = rspec.EPClan(PN.EPCLANS.NET_D, vmlan = usevms)
net_d.bandwidth = params.LINKBW
an_lte = rspec.EPClan(PN.EPCLANS.AN_LTE, vmlan = usevms)
an_lte.bandwidth = params.LINKBW

#
# Add the core EPC nodes
#

# epc-enablers node
epcen = PN.mkepcnode("epc", PN.EPCROLES.ENABLERS)
rspec.addResource(epcen)
mgmt.addMember(epcen)
net_a.addMember(epcen)

# pgw node
pgw = PN.mkepcnode("pgw", PN.EPCROLES.PGW)
rspec.addResource(pgw)
mgmt.addMember(pgw)
net_a.addMember(pgw)
net_b.addMember(pgw)

# sgw-mme-sgsn node
sgw = PN.mkepcnode("sgw", PN.EPCROLES.SGW_MME_SGSN)
rspec.addResource(sgw)
mgmt.addMember(sgw)
net_b.addMember(sgw)
net_d.addMember(sgw)

#
# Create the requested number of eNodeB nodes
#
for i in range(1, params.NUMENB + 1):
    ename = "enb%d" % i
    enb = PN.mkepcnode(ename, PN.EPCROLES.ENODEB, hname = ename)
    rspec.addResource(enb)
    mgmt.addMember(enb)
    net_d.addMember(enb)
    an_lte.addMember(enb)

#
# Now pop in the requested number of emulated clients (UEs).
#
for i in range(1, params.NUMCLI + 1):
    cname = "client%d" % i
    client = PN.mkepcnode(cname, PN.EPCROLES.CLIENT, hname = cname)
    rspec.addResource(client)
    mgmt.addMember(client)
    an_lte.addMember(client)

#
# Print and go!
#
pc.printRequestRSpec(rspec)
