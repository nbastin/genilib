#!/usr/bin/env python

"""A local ephemeral blockstore, specified using a parameterized profile. The size and the mountpoint can be customized when you instantiate the profile.

Instructions:
Log into your node, your `temporary` filesystem is in the directory you specified during profile instantiation.
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the emulab extensions library.
import geni.rspec.emulab

# Create a portal context, needed to defined parameters
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

pc.defineParameter("N", "Size of blockstore (GB)",
                   portal.ParameterType.INTEGER, 30)
pc.defineParameter("MPOINT", "Mountpoint for file system",
                   portal.ParameterType.STRING, "/foo")
params = pc.bindParameters()

node = request.RawPC("mynode")
bs = node.Blockstore("bs", params.MPOINT)
bs.size = str(params.N)

pc.printRequestRSpec(request)
