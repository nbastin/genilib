.. Copyright (c) 2017  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

CentOS 7
========

geni-lib is currently delivered only as a source repository via mercurial, although
dependencies are installed as proper packages using yum.

=======================
High-Level Dependencies
=======================

* Mercurial (http://mercurial.selenic.com)
* Python 2.7.x (http://www.python.org)
* OpenSSL
* LibXML

The above packages of course have their own dependencies which will be satisfied along the way.

====================
Install Dependencies
====================

These instructions install dependencies using yum - it is also possible to install the Python packages
using pip if you prefer.

The dependencies rely on EPEL (https://fedoraproject.org/wiki/EPEL), so
install that first.

::

   $ yum install epel-release

Now install the dependencies:

::

  $ yum install mercurial python-lxml python-requests \
    python-pip python-devel libffi-devel gcc openssl-devel

============
Get geni-lib
============
::

  $ hg clone http://bitbucket.org/barnstorm/geni-lib

=======
Install
=======
::

  $ cd geni-lib
  $ hg update -C 0.9-DEV
  $ pip install .

