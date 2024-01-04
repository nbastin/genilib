.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Querying the Federation
=======================

Before we can reserve resources, it is useful to know what resources are available across the
federation.  This tutorial will walk you through using the ``Context`` object you created in
the previous tutorial to communicate with aggregates known to ``geni-lib``.

Finding Aggregate Locations
---------------------------

``geni-lib`` contains a set of package files which have pre-built objects representing known
aggregates that are ready for you to use, contained within the following Python modules::

   geni.aggregate.exogeni
   geni.aggregate.instageni
   geni.aggregate.instageni_openflow
   geni.aggregate.opengeni
   geni.aggregate.protogeni
   geni.aggregate.vts

While these aggregates objects will likely cover your needs, ``geni-lib`` may of course not be
updated as frequently as new aggregates come online.  You can find a list of the current set of 
aggregates on the `GENI Wiki <http://groups.geni.net/geni/wiki/GeniAggregate>`_.

Getting Aggregate Information
-----------------------------

Given that we have our previously created ``Context`` object, and a wealth of aggregate objects
available to us, the GENI federation provides the ability to request two blocks of information
from each aggregate - the version information (which you may have seen briefly in a previous
tutorial), and a list of the advertised resources.

The result from ``getversion``, as we saw in the previous tutorial, is reasonably concise and
human readable (but also contains information about API versions and supported request formats
that you may need to extract in your tools).  The list of advertised resources is acquired using
the ``listresources`` call, and returns a large XML document describing the available resources,
which is relatively difficult to work with without a tool.

.. note::
  We will be using GENI AM API version 2 throughout this tutorial.  Some API call names will be
  different if you elect to interact with aggregates using AM API version 3 in the future.

* Lets start by getting an advertisement from a single aggregate.  If you built a custom
  context using Python code you will need to replace the code below to load your custom
  context::

   $ python
   >>> import geni.util
   >>> context = geni.util.loadContext()
   >>> import geni.aggregate.instageni as IGAM
   >>> ad = IGAM.Illinois.listresources(context)

  Now of course we have an advertisement (assuming everything went well) stored into a Python object,
  which is reasonably boring!

.. note::
  If you get timeouts or failures, you may want to try a different InstaGENI aggregate (this one may
  be particularly busy).  You can get a list of (mostly) aggregate objects by using the ``dir()`` command
  on the IGAM module - ``dir(IGAM)``.

* We can simply print out the advertisement raw text to see what the
  aggregate sent us::

   >>> print ad.text
   <rspec xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ......
   ...

  As you can see, even with this relatively small rack (5 hosts) the amount of data is significant.

* As ``geni-lib`` has parsed this advertisement into a more functional object, we have access to
  data objects instead of just raw xml.  For example, we can inspect the routable address space available
  at a site::

   >>> ad.routable_addresses.available
   167
   >>> ad.routable_addresses.capacity
   190

* You may have noticed that if you just print the ``routable_addresses`` attribute, you get nothing useful::

   >>> ad.routable_addresses
   <geni.rspec.pgad.RoutableAddresses object at 0x1717f10>

  While we are adding online documentation for ``geni-lib`` objects, there are many objects that are
  undocumented.  However, you can still gain some insight by using the ``dir()`` built-in to see
  what attributes are available::

   >>> dir(ad.routable_addresses)
   ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__',
   '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
   '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'available', 'capacity', 'configured']

  In general attributes starting with underscores are not useful to us, so we can see 3 attributes of
  value - ``available``, ``capacity``, and ``configured``.  In most cases their meanings should be
  obvious, so just knowing they exist even without documentation is quite helpful.

* There are also 3 iterators that are provided with ``Advertisement`` objects - ``nodes``, ``links``,
  and ``shared_vlans``::

   >>> for svlan in ad.shared_vlans:
   ...   print svlan
   ... 
   mesoscale-openflow
   exclusive-openflow-1755
   exclusive-openflow-1756
   exclusive-openflow-1757
   ...snip...
   
* While ``shared_vlans`` just iterates over a set of strings, ``node`` objects are much more complex
  and have many more attributes and nested data structures to allow you to fully inspect their state::

   >>> print dir(ad.nodes[0])
   [..., 'available', 'component_id', 'component_manager_id', 'exclusive', 'hardware_types', 'images',
   'interfaces', 'location', 'name', 'shared', 'sliver_types']

* Particularly useful for the puposes of binding requests to certain nodes at a given site is the
  component_id::

   >>> for node in ad.nodes:
   ...     print node.component_id
   ... 
   urn:publicid:IDN+instageni.illinois.edu+node+procurve2
   urn:publicid:IDN+instageni.illinois.edu+node+pc3
   urn:publicid:IDN+instageni.illinois.edu+node+pc5
   urn:publicid:IDN+instageni.illinois.edu+node+interconnect-ion
   urn:publicid:IDN+instageni.illinois.edu+node+pc1
   urn:publicid:IDN+instageni.illinois.edu+node+interconnect-campus
   urn:publicid:IDN+instageni.illinois.edu+node+pc2
   urn:publicid:IDN+instageni.illinois.edu+node+interconnect-geni-core
   urn:publicid:IDN+instageni.illinois.edu+node+pc4
   urn:publicid:IDN+instageni.illinois.edu+node+internet

* Spend some time inspecting the other attributes of each node.  You can get a specific node by using Python
  indexing on the ``nodes`` iterator::

   >>> node = ad.nodes[1]
   >>> node.component_id
   'urn:publicid:IDN+instageni.illinois.edu+node+pc3'

Iterating Over Aggregates
-------------------------

Often you will want to inspect a large number of aggregates (particularly if there are of an idential or
similar type) in order to find those that have availability in the resources that you require.  The aggregate
modules in ``geni-lib`` provide some convenience methods for assisting in this task::

    >>> import geni.aggregate.instageni as IGAM
    >>> for am in IGAM.aggregates():
    ...     print am.name
    ... 
    ig-cenic
    ig-cwru
    ig-clemson
    ig-cornell
    ig-ohmetrodc
    ig-gatech
    ig-gpo
    ig-illinois
    ...snip...

Using this iterator you can act on each aggregate in a given module with the same snippet of code.

* Lets try getting (and saving) the ``getversion`` output from each InstaGENI site::

    >>> import json
    >>> for am in IGAM.aggregates():
    ...     print am.name
    ...     verdata = am.getversion(context)
    ...     ver_file = open("%s-version.json" % (am.name), "w+")
    ...     json.dump(verdata, ver_file)
    ... 
    ig-cenic
    ig-cwru
    ig-clemson 
    ...snip...

  This will write out a file for every aggregate (barring any exceptions) to the current directory.

.. note::
  ``verdata`` in the above case is a Python ``dict`` object, so we need to pick a way to write it
  (in a human readable form) to a file.  In the above example we pick serializing to JSON (which is
  reasonably readable), but you could also use the ``pprint`` module to format it nicely to a file
  as a nice string.

Exercises
---------

We can now combine all of the above pieces, plus some Python knowledge, into some useful scripts.

#. Move the ``getversion`` code fragment above into a standalone script, and improve it to continue to
   the next aggregate if any exceptions are thrown by the current aggregate (unreachable, busy, etc.).

#. Write a script that prints out the number of availble routable IPs for each InstaGENI aggregate.
