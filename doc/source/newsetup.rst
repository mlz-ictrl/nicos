Setting up NICOS for a new instrument
=====================================

This is a checklist for setting up and installing NICOS for a new instrument.
Please suggest additions if needed!

Preparations
------------

* Clone the NICOS git repository.  Create an instrument branch with ``git
  checkout -b instname`` to record local changes independent of master.

* Install all pre-requisites.  If TACO is needed, make sure the Python client
  libraries are installed.

* Run ``make inplace`` and check if ``bin/nicos-demo`` works.  On X-less
  machines, use ``bin/nicos-demo -t``.  If something fails here, you might have
  missed a dependency.

* For good measure, run ``make test`` and make sure any failures are reported.

Setting up the new instrument customization
-------------------------------------------

* Copy the ``custom/skeleton`` directory to ``custom/instname``.

* Adapt the ``custom/instname/make.conf`` file.  It has comments what could be
  changed.

* Adapt the basic setups for the daemons in ``custom/instname/setups/special``;
  in particular, replace "localhost" by the instrument specific hostname.  See
  :doc:`services/index` for more reference.

* Adapt the basic system setup in ``custom/instname/setups/system.py``.  Make
  sure the data root on the "Exp" object is set correctly.

* Create more instrument setups as needed.

* For instruments that use the 2-D live data display, see
  ``custom/toftof/make.conf`` as a template how to set up the Make rules.

Building and installing
-----------------------

* Check if the build process works with ``make all``.

* Now you should be able to do an installation with ``make install``, or if the
  machine hostname does not include the instrument name, ``make install
  INSTRUMENT=instname``.

* Check the generated ``$ROOTDIR/nicos.conf`` for obvious errors.  See
  :ref:`nicosconf` for a description.

* If you did the install as root, the Makefile will have created a symlink to
  the init script (``$ROOTDIR/etc/nicos-system``) under
  ``/etc/init.d/nicos-system``, else you have to symlink it yourself.  Check if
  the init script works with ``/etc/init.d/nicos-system start``.

* Commit code changes and push to gerrit (more likely, use ``git format-patch
  origin/master`` and commit/push the patches on a machine where you have your
  public key).  Instruct instrument people to always change the files in the
  checkout and commit them.

Adding setups and libraries
---------------------------

* Setups can be created in ``custom/instname/setups`` and installed normally.
  Modules go under ``custom/instname/lib``.

* To test setups and modules with the checkout instead of the installed copy,
  copy the ``nicos.conf`` file from the install dir to the checkout dir, and
  change the ``setups_path`` entry::

    [nicos]
    ...
    setups_path = custom/instname/setups

* Modules like ``custom/instname/lib/foo.py`` can be imported as
  ``nicos.instname.foo`` (or, in setups, also ``instname.foo``).

GUI configuration
-----------------

* On machines that should run only the GUI, use ``make install-gui`` instead of
  ``make install``.

* A custom ``defconfig.py`` can go under ``custom/instname/gui/defconfig.py``.
