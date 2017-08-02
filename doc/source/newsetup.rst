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

* Install all pre-requisites (see :doc:`install`).

* Check if ``bin/nicos-demo`` works.  On X-less machines, use ``bin/nicos-demo
  -MT``.  If something fails here, you might have missed a dependency.

* For good measure, run ``make test`` and make sure any failures are reported.

Setting up the new instrument customization
-------------------------------------------

* Copy the ``nicos_demo/skeleton`` directory to the new custom package,
  ``nicos_<facility>/<instrument>``.

* Adapt the ``nicos_<facility>/<instrument>/nicos.conf`` file.  It has comments
  for values that might need to be changed.

* Adapt the basic setups for the daemons in
  ``nicos_<facility>/<instrument>/setups/special``; in particular, you probably
  want to replace "localhost" by the instrument specific hostname.  See
  :doc:`services/index` for more reference.

* Adapt the basic system setup in
  ``nicos_<facility>/<instrument>/setups/system.py``.  Make sure the data root
  on the "Exp" object is set correctly.

* Create more setup files as needed, and do not hesitate to refer to other
  instruments' setup files for that!

Building and installing
-----------------------

* Now you should be able to do an installation with ``make install
  PREFIX=<installation_path>``.

* Check the generated ``$PREFIX/nicos.conf`` for obvious errors and adapt it.
  See :ref:`nicosconf` for a description.

* If you want the init script to be recognized by the system, create a symlink
  to ``$PREFIX/etc/nicos-system`` in ``/etc/init.d``.  Similarly, you can add
  ``$PREFIX/bin`` to ``$PATH``, or create links to them somewhere in ``$PATH``,
  e.g. ``/usr/local/bin``.  Check if the init script works with
  ``/etc/init.d/nicos-system start``.

* Commit code changes and push to gerrit (or use ``git format-patch
  origin/master`` or ``origin/release-X.Y`` and commit/push the patches on a
  machine where you have your public key).  Instruct instrument people to always
  change the files in the checkout and commit them.

Adding setups and libraries
---------------------------

* Setups can be created in ``nicos_<facility>/<instrument>/setups``.  Modules
  for devices go under ``nicos_<facility>/<instrument>/devices``.  The script
  ``tools/check_setups`` is very helpful when writing new setups.  It can be
  called directly from the checkout.

* To test setups and modules with the checkout instead of the installed copy,
  you can set the environment variable ``INSTRUMENT`` to
  ``nicos_<facility>.<instrument>``.

* Modules like ``nicos_<facility>/<instrument>/devices/foo.py`` can be imported
  as ``nicos_<facility>.<instrument>.devices.foo``.

GUI configuration
-----------------

* A custom GUI config file can go under
  ``nicos_<facility>/<instrument>/guiconfig.py``, see :ref:`gui-config`.  It is
  easiest to use the one under ``nicos_demo/demo`` as a starting point.

* Custom Python modules (e.g. with Panels) should go under
  ``nicos_<facility>/<instrument>/gui`` to be importable under
  ``nicos_<facility>.<instrument>.gui``.
