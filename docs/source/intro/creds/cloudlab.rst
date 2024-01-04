.. Copyright (c) 2016-2017  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Getting Credentials from the CloudLab Portal
============================================

CloudLab only provides your x509 certificate from the web interface.  You will
have to provide your own SSH public key for use with `geni-lib` when you set
up your context for using reserved resources.

* Log in to the `CloudLab Portal <https://www.cloudlab.us/login.php>`_.
* From the **<your-username>** dropdown at the top right of the interface, select the
  **Download Credentials** option
* Save this text (either via copy/paste or **Save As...** in your brower) to
  a file called ``cloudlab.pem`` for use when creating your context.

You will also need to take note of the projects of which you are a member, in order to
set up your context.  You can view your projects by clicking on the **Membership** tab
on the user dashboard interface.
