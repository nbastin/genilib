.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Creating a Custom Context
=========================

In order to communicate with any federation resource using ``geni-lib`` you need to construct
a ``Context`` object that contains information about the framework you are using (for example
ProtoGENI, Emulab, GENI Clearinghouse, etc.), as well as your user information (SSH keys,
login username, federation urn, etc.).  You can use the ``context-from-bundle`` script that
comes with ``geni-lib`` to create a context from an ``omni.bundle`` provided by the GENI Portal
as documented in the "Importing a Context from the GENI Portal" tutorial, or you can create one
using a small Python module which allows for more configurability, and we illustrate that
method here.

* To start, we will create a new Python file called ``mycontext.py`` and (inside the directory
  containing your ``geni-lib`` clone) import the necessary modules to start building your own
  context using your favorite editor::

   from geni.aggregate import FrameworkRegistry
   from geni.aggregate.context import Context
   from geni.aggregate.user import User


* Now we add a function that you will call each time you want to create your context (using the 
  GENI Clearinghouse as the default framework)::

   def buildContext ():
     framework = FrameworkRegistry.get("portal")()
  
* You need to give the framework instance the location of your user certificate and key files::

     framework.cert = "/home/user/.ssh/portal-user.pem"
     framework.key = "/home/user/.ssh/portal-user.key"

.. note::
  You may only have one file which contains both items - you can use the same path for both
  variables if this is the case.

* Now we need to define an account and SSH key(s) that will be used to access reserved compute resources::

     user = User()
     user.name = "myusername"
     user.urn = "urn:publicid:IDN+ch.geni.net+user+myusername"
     user.addKey("/home/user/.ssh/geni_dsa.pub")

  We create a ``User()`` object, give it a name (no spaces, commonly a username), and the user URN.
  We then add an SSH public key that will be installed on any compute resources that you reserve
  in order to authenticate with those resources.

* Next we make the parent ``Context`` object and add our user and framework to it, with a default project::

     context = Context()
     context.addUser(user, default = True)
     context.cf = framework 
     context.project = "GEC21"

  This adds the user we created above, sets the control framework (``cf``), and sets your default project.

* You now want to return this object so that you can use this function every time you need a context::

     return context

Now to see the complete code in one block::

   from geni.aggregate import FrameworkRegistry
   from geni.aggregate.context import Context
   from geni.aggregate.user import User

   def buildContext ():
     framework = FrameworkRegistry.get("portal")()
     framework.cert = "/home/user/.ssh/portal-user.pem"
     framework.key = "/home/user/.ssh/portal-user.key"

     user = User()
     user.name = "myusername"
     user.urn = "urn:publicid:IDN+ch.geni.net+user+myusername"
     user.addKey("/home/user/.ssh/geni_dsa.pub")

     context = Context()
     context.addUser(user, default = True)
     context.cf = framework 
     context.project = "GEC21"

     return context

You can dynamically alter this object at any time, but your defaults will serve your purposes for the vast
majority of your use cases.

Test It Out!
------------

Now we can take your newly written file, instantiate our context, and query an aggregate::

   $ python
   >>> import mycontext
   >>> context = mycontext.buildContext()
   >>> import geni.aggregate.instageni as IG
   >>> import pprint
   >>> pprint.pprint(IG.GPO.getversion(context))
   {'code': {'am_code': 0,
             'am_type': 'protogeni',
             'geni_code': 0,
             'protogeni_error_log': 'urn:publicid:IDN+instageni.gpolab.bbn.com+log+abedbcc20e6defe716eb83b8586c7e08',
             'protogeni_error_url': 'https://boss.instageni.gpolab.bbn.com/spewlogfile.php3?logfile=abedbcc20e6defe716eb83b8586c7e08'},
   ...snip...

You should get a large structure of formatted output telling you version and configuration
information about the GPO InstaGENI aggregate.  If you get any errors read them thorougly and
review what they may be telling you about any mistakes you may have made.  You can also ask your
instructor (if at a GEC / Live Tutorial), or send a message to the
`geni-users <https://groups.google.com/forum/#!forum/geni-users>`_ google group.
