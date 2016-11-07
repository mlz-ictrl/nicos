Setting up NICOS for a new instrument
=====================================

This is a checklist for setting up and installing NICOS for a new instrument.
Please suggest additions if needed!

Preparations
------------

* Clone the NICOS git repository.  Check out either ``master`` (if the
  instrument should reflect the development version) or ``release-X.Y`` (if it
  should be based on a released version).  Create a working branch with ``git
  checkout -b work-X.Y`` to record local changes independent of the upstream
  branch.

* Install all pre-requisites (see :ref:`requirements`).  If TACO is needed, make
  sure the Python client libraries are installed.

* Run ``make`` and check if ``bin/nicos-demo`` works.  On X-less
  machines, use ``bin/nicos-demo -t``.  If something fails here, you might have
  missed a dependency.

* For good measure, run ``make test`` and make sure any failures are reported.

Setting up the new instrument customization
-------------------------------------------

* Copy the ``custom/skeleton`` directory to ``custom/instname``.

* Adapt the ``custom/instname/nicos.conf`` file.  It has comments for values
  that might need to be changed.

* Adapt the basic setups for the daemons in ``custom/instname/setups/special``;
  in particular, you probably want to replace "localhost" by the instrument
  specific hostname.  See :doc:`services/index` for more reference.

* Adapt the basic system setup in ``custom/instname/setups/system.py``.  Make
  sure the data root on the "Exp" object is set correctly.

* Create more setup files as needed, and do not hesitate to refer to other
  instruments' setup files for that!

Building and installing
-----------------------

* Check if the build process works with ``make all``.

* Now you should be able to do an installation with ``make install``, or if the
  machine hostname does not include the instrument name, ``make install
  INSTRUMENT=instname PREFIX=<installation_path>``.

* Check the generated ``$PREFIX/nicos.conf`` for obvious errors.  See
  :ref:`nicosconf` for a description.

* If you did the install as root, the Makefile will have created a symlink to
  the init script (``$PREFIX/etc/nicos-system``) under
  ``/etc/init.d/nicos-system``, else you have to symlink it yourself.  Check if
  the init script works with ``/etc/init.d/nicos-system start``.

* Commit code changes and push to gerrit (or use ``git format-patch
  origin/master`` or ``origin/release-X.Y`` and commit/push the patches on a
  machine where you have your public key).  Instruct instrument people to always
  change the files in the checkout and commit them.

Adding setups and libraries
---------------------------

* Setups can be created in ``custom/instname/setups`` and installed normally.
  Modules go under ``custom/instname/lib``.  The script ``tools/check_setups``
  is very helpful when writing new setups.  It can be called from the checkout,
  and is also automatically run on ``make install``.

* To test setups and modules with the checkout instead of the installed copy,
  you can set the environment variable ``INSTRUMENT`` to the instrument name.

* Modules like ``custom/instname/lib/foo.py`` can be imported as
  ``nicos.instname.foo`` (or, in setups, also ``instname.foo``).

GUI configuration
-----------------

* On machines that should run only the GUI, use ``make install-gui`` instead of
  ``make install``.

* A custom GUI config file can go under ``custom/instname/guiconfig.py``,
  see :ref:`gui-config`.  It is easiest to use the one under ``custom/demo``
  as a starting point.

* Custom Python modules (e.g. with Panels) should go under
  ``custom/instname/lib/gui`` to be importable under ``nicos.instname.gui``.
