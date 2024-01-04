.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Windows 7 (32-bit)
==================

These instructions may work on later versions of Windows, and/or 64-bit versions, but they have not been tested.

=========================
Installation Dependencies
=========================

* Mercurial 3.8.2 (http://mercurial.selenic.com/wiki/Download)
* Python 2.7.11 (http://www.python.org)

.. note::
  Make sure to set the installation option to add Python.exe to your PATH, or you will have to do this
  manually later, or type out the full path to python during ``geni-lib`` installation and use.

=====================
Install / Basic Setup
=====================

* Install the above dependencies

* Open a Powershell command line and clone the geni-lib repository::

   C:\> mkdir C:\Development
   C:\> cd C:\Development
   C:\Development> hg clone https://bitbucket.org/barnstorm/geni-lib
   C:\Development> cd geni-lib
   C:\Development\geni-lib> hg update -C 0.9-DEV

* Install some dependencies directly::

   C:\Development\geni-lib> pip install cryptography lxml wrapt

* Install the main `geni-lib` packages:: 

   C:\Development\geni-lib> python setup.py install

.. note::
  (The location of the ``geni-lib`` clone can be changed, just alter these paths accordingly)

Congratulations, you are now ready to launch ``python`` and import geni lib modules!


=====================
Extended Dependencies
=====================

Some of the applications in the ``tools/`` directory require additional dependencies.  For the most part
these dependencies can be installed using ``pip``, but ``pip`` is not included in the Python 2.7
distribution by default on windows.

You can install ``pip`` on Windows 7 and later by launching ``Powershell`` (not ``cmd.exe``) and doing::

  PS C:\> $client = new-object System.Net.WebClient
  PS C:\> $client.DownloadFile("http://bootstrap.pypa.io/get-pip.py", "C:/Development/get-pip.py")

Note that the second argument must be a valid full path.  Remember where you placed this file.

Now, open ``cmd.exe`` and run the batch file that sets up the geni-lib environment (or use your previously
created shortcut), and do the following::

  C:\> cd C:\Development
  C:\Development> python get-pip.py

Now you can use ``pip`` to install new dependencies that the additional tools may require.
