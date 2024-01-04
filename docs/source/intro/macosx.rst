.. Copyright (c) 2015-2016  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

MacOS X 10.10.x / 10.11.x
=================================

These installations require the use of HomeBrew (http://brew.sh).  If you use
MacPorts or a different manager for installing open source tools on your system
you will need to satisfy the dependencies using your tool of choice.

.. note:: 
  These instructions have not been tested on older versions of MacOS X

=========================
Installation Dependencies
=========================

* HomeBrew (http://brew.sh)
* Apple Command Line Tools for XCode (normally downloaded as part of Brew install)

===============
Install / Setup
===============

Using HomeBrew (accessible via the ``brew`` command in your terminal, once you have it installed) 
we will install the necessary tools and library dependencies for typical ``geni-lib`` use::

  $ brew install mercurial
  $ brew install python

.. note::
  You will now have two version of ``python`` installed on your system - the one that Apple ships
  with your computer, and the one that we have now installed via ``brew``.  Only the ``brew``-installed
  ``python`` will work for running ``geni-lib`` scripts, which can be launched by running
  ``/usr/local/bin/python`` or by changing your ``$PATH`` variable to have ``/usr/local/bin`` as the
  first entry (by editing ``~/.profile``, typically).

============
Get geni-lib
============

You can place the geni-lib repository anywhere on your system that you prefer.

::

  $ hg clone http://bitbucket.org/barnstorm/geni-lib

================
Install geni-lib
================

We can now install ``geni-lib`` into your Python environment::

  $ cd geni-lib
  $ hg update -C 0.9-DEV
  $ python setup.py install

Congratulations, you are now ready to launch ``python`` and import geni lib modules!
