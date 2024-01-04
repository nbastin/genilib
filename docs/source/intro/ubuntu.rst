.. Copyright (c) 2015-2018  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Ubuntu 14.04
============

Release versions of geni-lib are delivered via `PyPI <pypi.org>`_, but some system dependencies
must be supplied, typically through the use of `apt`.

=======================
High-Level Dependencies
=======================

* Python 2.7.x (http://www.python.org)
* Pip
* OpenSSL
* LibXML

The above packages of course have their own dependencies which will be satisfied along the way.

.. warning::
  The version of `pip` supplied via apt packages for Ubuntu 14.04 for Python 2.x is sufficiently broken
  that it is unlikely to be able to install `geni-lib` (or many other packages).  The instructions
  below install `pip` outside of the package management system, using the most up-to-date installer.  If
  you are already using `virtualenv` or otherwise maintain a sane Python environment you likely do not
  need to install a new `pip`.

====================
Install Dependencies
====================
::

  $ sudo apt-get update
  $ sudo apt-get install --no-install-recommends python libxml2 libssl1.0.0

  $ wget https://bootstrap.pypa.io/get-pip.py
  $ sudo python2 get-pip.py

=======
Install
=======
::

  $ pip install geni-lib

.. note::
  You may need to install with `sudo` if you are attempting to install system-wide.
