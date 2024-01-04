.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Creating a Request for a Single VM
=================================

This example walks through the basic of creating an RSpec (xml file) requesting
a single VM from a compute aggregate.  This example does not require that `geni-lib`
is configured with user credentials or keys - it will create an XML file that you
can feed into another tool such as `Jacks` or `Omni` (other examples cover how to make
this request using `geni-lib` itself).

.. note::
  You can find the complete source code for this example in a single file in the
  `geni-lib` distribution in `samples/onevm.py`.

Walk-through
------------

* Since we only want to output the XML of the request, we need very few imports::

   import geni.rspec.pg as PG
   import geni.rspec.egext as EGX
   import geni.rspec.igext as IGX

.. note::
  While the first module is named 'pg' (after ProtoGENI), the base rspec format is 
  common across compute aggregates and all will use the same `Request`
  container, although the resources in that container will differ based on what
  is available at a given site.

* Now we need to create the basic `Request` container::

   r = PG.Request()

* Unfortunately there is no unified VM object for all compute aggregates, so you
  will need to know which "flavor" of compute aggregate you intend to use (most
  commonly either InstaGENI or ExoGENI).

.. note::
  In later examples you will see how, if you are using `geni-lib` to make your
  reservations directly with the aggregates, you can indeed create a single
  VM request that can be used across aggregate "flavors".

* Now we will allocate a VM object that can be added to our request (examples
  shown here for both ExoGENI and InstaGENI)::

   # ExoGENI
   exovm = EGX.XOSmall("vm1")

   # InstaGENI
   igvm = IGX.XenVM("vm1")

.. note::
  The only required configuration for each resource is the `name` argument
  that is passed to the constructor.  These names must be unique within a
  single site, but can be reused at different sites.

* For the purposes of this example we will only add the InstaGENI VM to the actual
  request that we will produce::

   r.addResource(igvm)

* Now that we have a request that contains a resource, we can write the XML to disk
  that represents this request::

   r.writeXML("onevm-request.xml")

