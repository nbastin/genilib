.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

VTS: Basic WAN Topology
=======================

This example walks through creating a two-site WAN topology with one forwarding
element at each site.  Like all VTS reservations that require compute resources,
the resources for each site will come from two different aggregate managers.
This example also employs further sequencing constraints in order to build the
WAN circuit.

.. image:: images/vts-simplewan.*

In order to build a circuit between two sites those sites need to share a
common **circuit plane**.  This is simply a named substrate that both sides have
a common attachment to.  In this tutorial we will use the ``geni-al2s``
circuit plane, which is currently available at most GENI VTS sites and replaces the
``geni-mesoscale`` circuit plane that is available at some sites but is being phased
out.

.. note::
  This example requires that you have set up a valid context object with GENI
  credentials.

For this example we'll use InstaGENI compute resources, but this would work
for ExoGENI sites that have VTS support as well if you change the InstaGENI
imports to the relevant ones for ExoGENI.

Set up VTS Slivers
------------------

We will first set up VTS slivers at both sites, before creating the local compute
resources.  This is not a strict requirement - you must always set up the VTS sliver
at a site before the compute sliver, but you can request the compute sliver at a
site before requesting the next site VTS sliver if that better fits your workflow.

In this example we will save the VTS manifests for later use to get compute
resources, in case your interactive Python session needs to be restarted.

* We need to set up basic imports to create requests and send them to the
  aggregate::

   import geni.rspec.pg as PG
   import geni.rspec.igext as IGX
   import geni.rspec.vts as VTS

   import geni.aggregate.instageni as IGAM
   import geni.aggregate.vts as VTSAM

* Here we also set up the slice name you're going to use, as well as the
  context object that specifies your credential information.  If you set up
  your ``geni-lib`` using the GENI Portal Import method, the code below will
  directly work.  If you built a custom context using your own Python code
  you will need to replace the code below to load your custom context::

   import geni.util

   context = geni.util.loadContext()
   SLICENAME = "my-slice-name"  # Change this to be your slice name

.. note::
  If you do not have a slice available in your project, you may need to go back
  to the GENI Portal web interface and create a new slice.  Also if you have multiple
  projects you may need to modify which one is being used by setting the
  ``context.project`` attribute.

* VTS reservations are typically a multistage process, where the VTS resources at
  a site must be reserved before the compute resources, or neighbour site VTS
  resources, and the results from the earlier reservations will be used to seed
  data in all subsequent reservations. In the case of WAN reservations we will
  need advertisement information from the *remote* VTS site we intend to connect
  our circuits to::

   remote_ad = VTSAM.NPS.listresources(context)

* We need to search this remote advertisement for information that describes the
  endpoint we want to use for our chosen circuit plane::

   for cp in remote_ad.circuit_planes:
     if cp.label == "geni-al2s":
       remote_endpoint = cp.endpoint

* We now start to build our primary site VTS request rspec::

   s1r = VTS.Request()

* As in previous tutorials we will select a default L2 learning image for our
  forwarding elements::

   image = VTS.OVSL2Image()

* We the instantiate a single forwarding element with this image, and request
  a local circuit to connect to our VM, as well as a WAN circuit to connect to
  the remote site::

   felement = VTS.Datapath(image, "fe0")
   felement.attachPort(VTS.LocalCircuit())
   wan_port = felement.attachPort(VTS.GRECircuit("geni-al2s", remote_endpoint))
   s1r.addResource(felement)

.. note::
  We have chosen to use a GRE Circuit here to reach the remote site, although
  other types might be available.  Each site advertises a list of supported
  encapsulation types for each circuit plane, allowing you to choose the one
  that best suits your needs based on performance and packet overhead.

* Now our request object is complete for our first site, so we can contact the
  aggregate manager and make the reservation::

   ukym = VTSAM.UKYPKS2.createsliver(context, SLICENAME, s1r)
   
.. note::
  If you are at an in-person tutorial you may need to replace ``VTSAM.UKYPKS2``
  with the aggregate you have been given on your tutorial worksheet.

* We will write out our returned manifest to disk in case we need to restart
  our Python session::

   ukym.writeXML("vts-ukypks2-manifest.xml")

* Now we will start building the VTS request at the remote site::

   s2r = VTS.Request()

* The basic parts of the request are the same at each site::

   felement = VTS.Datapath(image, "fe0")
   felement.attachPort(VTS.LocalCircuit())
   s2r.addResource(felement)

* Now we need to attach one port to our forwarding element that connects to the
  remote site that we have already configured::

   felement.attachPort(VTS.GRECircuit("geni-al2s", ukym.findPort(wan_port.clientid).local_endpoint))

  This searches our previous manifest for the WAN port we have already defined,
  and gathers the endpoint information to put in a remote request.  The combination
  of this inforamtion will create a complete WAN circuit.

* Having created our request, we send it to the aggregate manager to reserve our
  resources, and write the output to a file::

   npsm = VTSAM.NPS.createsliver(context, SLICENAME, s2r)
   npsm.writeXML("vts-nps-manifest.xml")


Set up InstaGENI Compute Slivers
--------------------------------

As we have two sites, we will need to set up our compute slivers at both sites, using
the manifests returned from each VTS request.  We want to set up IP addresses that we
will use on both sides of our WAN topology::

   IP = "10.50.1.%d"
   NETMASK = "255.255.255.0"

* Each request is relatively simple, containing only a single VM connected to a single
  VTS port, pulled from the site VTS manifest::

   ukyr = PG.Request()
   
   for idx,circuit in enumerate(ukym.local_circuits):
     vm = IGX.XenVM("vm%d" % (idx))
     intf = vm.addInterface("if0")
     intf.addAddress(PG.IPv4Address(IP % (1), NETMASK))
     ukyr.addResource(vm)
     lnk = PG.Link()
     lnk.addInterface(intf)
     lnk.connectSharedVlan(circuit)
     ukyr.addResource(lnk)

The code above is the same as in earlier tutorials, which you can refer to for more
thorough explanation.

* Now we make the reservation::

   ukyigm = IGAM.UKYPKS2.createsliver(context, SLICENAME, ukyr)
   geni.util.printlogininfo(manifest=ukyigm)

* We execute nearly identical code for the second site (note the IP address change)::

   npsr = PG.Request()
   
   for idx,circuit in enumerate(npsm.local_circuits):
     vm = IGX.XenVM("vm%d" % (idx))
     intf = vm.addInterface("if0")
     intf.addAddress(PG.IPv4Address(IP % (2), NETMASK))
     npsr.addResource(vm)
     lnk = PG.Link()
     lnk.addInterface(intf)
     lnk.connectSharedVlan(circuit)
     npsr.addResource(lnk)

* Now we make the second site reservation::

   npsigm = IGAM.NPS.createsliver(context, SLICENAME, npsr)
   geni.util.printlogininfo(manifest=npsigm)

* In a few minutes you should be able to log into your VMs with the info printed
  out by the above step and send test traffic (ping, etc.) between the VMs across
  your VTS WAN topology.

* Once you are done using your topology and exploring the tutorial, please delete
  all the resources you have reserved::

   IGAM.NPS.deletesliver(context, SLICENAME)
   IGAM.UKYPKS2.deletesliver(context, SLICENAME)
   VTSAM.NPS.deletesliver(context, SLICENAME)
   VTSAM.UKYPKS2.deletesliver(context, SLICENAME)
