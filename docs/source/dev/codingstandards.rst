.. Copyright (c) 2017  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Coding Conventions
==================

There is a ``pylint.rc`` file that is tweaked for most of the project style.  It is not perfect, but is a good
check to run immediately after cloning, and then right before a pull request (as ``pylint`` will report the
difference in compliance once you have run it once).  The script ``lint.sh`` in the root directory will run
``pylint`` with this file over the proper directory tree.

* All indentation uses spaces
* Indents are 2 spaces
* Exceptions that exist only for specializing names should be written on one line::

    class MyCommonException(Exception):
      def __init__ (self, some_data):
        ...
      def __str__ (self):
        ...

    class SpecificNameOne(MyCommonException): pass
    class SpecificNameTwo(MyCommonException): pass

  There is an example of this use case in ``geni.aggregate.pgutil``

* Maximum line length is 132 characters
* Class-level and global variables are **highly** discouraged
* Never use bare ``except:`` clauses
* Do not use ``print``


Pattern Conventions
===================

* Exception hierarchies are highly encouraged, as they allow users to dispatch their own scripting on the
  the type of exception, rather than having a single exception with varying messages or ``errno``-like mechanics.
* Anything that imports ``cryptography`` should never be imported at module level.  Always import crypto and network
  functionality inside functions, as this minimizes the dependencies for users who are only generating or parsing
  XML.
* All public attribute storage types should be internally consistent for reads.  If you want to support setting an
  underlying float storage type using a string or integer, use a property.  Non-public attributes should also follow
  this rule unless there is a really good reason not to.
* If you can foresee a problem in the future, but don't have time to fix it now, at least leave a ``# TODO`` note.
* At the moment many ``geni-lib`` instances are re-entrant.  However, while we should support this where possible,
  it is not required nor will it be guaranteed to users.


Philosophy Notes
================

``geni-lib`` is a surprisingly useful tool for end-users.  However, that does not mean it is designed as a user
tool.  As it is a library, constraints and "convenience" can always be wrapped around it, but they can't be removed
if the library is too opinionated at a base level.  Convenience is generally acceptable if the underlying
functionality can be directly accessed by the user should they want to avoid whatever level of "help" is being
offered.

* Do not provide Magic(tm) to users in the base API.  ``geni-lib`` should not go out of its' way to protect the user
  from building a request that we believe the be impossible to satisfy, or from passing "bad" data to AM API calls.
* AM wrappers provide some basic level of sanity checking of input values (specifically for POAs in the VTS
  support).  This is acceptable as there is a lower-level API a user may use if they want to ignore those
  checks (``geni.minigcf.amapi3``).  That being said, this level of convenience should be limited.
* While we support IronPython and Jython, those ``geni-lib`` users should still prefer ``multiprocessing`` for
  parallel execution, instead of ``threading``.
* Providing convenience shouldn't extend to essentially providing new tools - it's hard to say where this line is,
  but providing too much tool-like functionality in ``geni-lib`` puts pressure on both the release schedule and
  the versioning and API stability.


Things That Don't Belong
========================

For legacy reasons, ``geni-lib`` includes code that either doesn't belong entirely, or is in the wrong place.
Anything enumerated here should not be referred to as an example of good practice moving forward:

* ``geni.aggregate.*`` - This package is a mess.  Frameworks need to move out somewhere else, and the AM
  locations should not be in the code (they should be loaded from data files which can be updated independently
  of the ``geni-lib`` code).  ``context`` also doesn't belong here, once framework support moves.
* ``geni.rspec.pg*`` - The "pg" rspec is now the "GENI" rspec, and we should rename accordingly.  Things that are
  *actually* part of Emulab and not the base functionality should live in extensions.
