.. Copyright (c) 2017  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Creating a Context from Cloudlab Credentials
============================================

You can use the generic `build-context` tool included with `geni-lib` to build a context
definition for use with Cloudlab.  You will need the following files before you start:

* A Cloudlab x509 credential in .pem format
* The name of a project of which you are a member
* An ssh public key

Given the above, you can run the `build-context` tool directly::

  build-context --type cloudlab --cert /path/to/cloudlab.pem \
    --pubkey /path/to/ssh_key.pub --project projectname

Replacing the paths and project name with values appropriate for your environment.  This
will create a context definition which will be loaded automatically when using the `genish`
or `ipython` interfaces, and can be loaded into your custom scripts using
`geni.util.loadContext()`.
