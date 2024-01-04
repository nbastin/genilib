.. Copyright (c) 2017  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Supported Use Cases
===================

This document makes a weak stab at articulating the use cases which ``geni-lib`` is expected to support.  This is in
an attempt to provide guidance on architecture decisions for new features to make sure we don't break existing use
cases.


Exact Request Rspec Creation
----------------------------

The most basic use of ``geni-lib`` is to write a small script whose sole purpose is to create a single rspec, from
a simple evaluation of end-to-end instructions.  Such a use may involve basic parameters, but does not take input from
active querying of the federation.  This provides code that is easy to edit to change behaviour, but otherwise is
indistinguishable from editing an XML file.

This use case should not be complicated.


Modular / Multi-rspec Creation
------------------------------

It is often useful to provide subtrees of resource definitions that are not complete Request objects (a specific VM
disk image, memory/disk configuration and execution scripts, etc). These trees can then be composed into Request
objects for novel topologies.  In this vein, it is also useful to create more than one Request at a time, composing
them together for issuing to separate aggregates.


Federation Querying
-------------------

It is valuable and must be possible for users to hold in memory multiple advertisement and manifest rspec wrappers
at the same time.  At the very minimum the following resource tuples must be able to exist in memory at the same
time:

* (site, advertisement)
* (site, slice, manifest)

At the moment any number of instances of these combinations are supported - any change to restrict these instances
to being unique (e.g. only one advertisement per site at a time, etc.) will have to be well justified.


Aggregate / Clearinghouse Actions
---------------------------------

Users should be able to operate on many aggregates and clearinghouses in the same script.  There is a current (and likely
ongoing) requirement that the user only be configured to use one control framework (and credentials) at a time.  If
more than one CH supports the same credentials and API, they should be able to be used concurrently, as AMs also must.
Users are responsible for completing all previous credentialed federation actions before changing the CF or credentials
their context refers to.
