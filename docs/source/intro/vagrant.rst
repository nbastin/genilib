.. Copyright (c) 2016-2018  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Vagrant
=======

``geni-lib`` can be installed on any platform that supports Vagrant using the instructions
below.

Two variants of the Vagrant environment can be created - a *lite* version that only contains ``geni-lib``
and should only be used by developers that are accustomed to working with Vagrant or similar environments,
and a *lab* version that is more fully-featured and should be used by new ``geni-lib`` users or those
using ``geni-lib`` for a class or conference tutorial.

The documentation here currently only covers the *lab* version.

The Vagrant VM created by this process automatically sets up your geni-lib context and
provides a web interface for creating `Jupyter <http://jupyter.org>`_ notebooks using GENI resources,
as well as a web-based interface for accessing the VM shell.

.. note::
  See the Configurable Options section below for environment variables which can tweak the settings of the
  VM environment that is created.

=========================
Installation Dependencies
=========================

Install these dependencies before creating the Vagrant VM.

* VirtualBox (https://www.virtualbox.org/wiki/Downloads)
* Vagrant (https://www.vagrantup.com/downloads.html)

=================================
Set up your geni-lib VM directory
=================================

* Create a directory on your system named ``genivm`` to hold your GENI environment
* Copy your ``omni.bundle`` to this directory
* Download the ``geni-lib`` Vagrant setup file to this directory from
  https://bitbucket.org/barnstorm/geni-lib/raw/tip/support/Vagrantfile-lab and rename it to be called
  ``Vagrantfile``

 * On systems with ``curl`` (MacOS X, Linux) you can use the following command::

    curl https://bitbucket.org/barnstorm/geni-lib/raw/tip/support/Vagrantfile-lab -o Vagrantfile
  
 * On Windows systems with Powershell you can use the following::

    PS C:\genivm> $client = new-object System.Net.WebClient
    PS C:\genivm> $client.DownloadFile("https://bitbucket.org/barnstorm/geni-lib/raw/tip/support/Vagrantfile-lab", "C:/genivm/Vagrantfile")

   .. note::
      The full path for the destination *must* be specified in the second argument to `DownloadFile`

* Create your vagrant vm using ``vagrant up`` in this directory

.. note::
  This may take a long time (20+ minutes) depending on the speed of your internet connection

==============================
Load the Jupyter web interface
==============================

* Open any web browser and load ``http://localhost:8900``
* In the upper right-hand corner of the UI, choose ``New->(Notebooks) Python 2`` from the dropdown menu
* In the new notebook enter ``%load_ext genish`` in the first cell and enter your key passphrase if necessary
  (otherwise just hit enter to skip the passphrase entry)

=========================
Accessing the VM Terminal
=========================

You may often want to access the VM command line for accessing your GENI resources, updating ``geni-lib``,
etc.  While you can use `vagrant ssh` on some platforms, this doesn't work very well on Windows, so the VM
provides a web-based mechanism for accessing the VM shell directly.

* Open any web browser and load ``http://localhost:8900``
* In the upper right-hand corner of the UI, choose ``New->Terminal`` from the dropdown menu

This will automatically log you into the VM and provide you a shell interface for using the VM OS directly.

====================
Configurable Options
====================

The following environment variables can be set to change the parameters under which the VM is created when
`vagrant up` is first executed:

+---------------+-------------+------------------------------------------------------------+
| **Name**      | **Default** | **Description**                                            |
+---------------+-------------+------------------------------------------------------------+
| ``glv_port``  | 8900        | Local port the Jupyter web interface will be exposed on    |
+---------------+-------------+------------------------------------------------------------+
| ``glv_ram``   | 1024        | Amount of memory available to the VM                       |
+---------------+-------------+------------------------------------------------------------+
| ``apt_cache`` | *unset*     | URL of proxy used for apt downloads                        |
+---------------+-------------+------------------------------------------------------------+
| ``pypi_test`` | *unset*     | If set, use the test PyPI repository instead of production |
+---------------+-------------+------------------------------------------------------------+

