Test scripts
------------

The traditional NICOS unit and integration test suite covers a wide range of
functionality.

However, to test instrument specific code, it is also quite helpful to have
special scripts, which should run successfully after maintainance at the
instruments either for hardware or for software.

These tests are designed for 2 applications:

- Allow the instrument scientists to test their instruments after a shutdown
  and/or update of the NICOS system. This isn't always easy, but the idea is
  that the instrument scientists know best what's important to test for a stable
  operation of the instrument.
- Use the same tests to run them in the test suite to see if the code is still
  working, at least in the simulation/dry run mode.  As a side effect, this
  ensures that the dry run will work at the instrument as well.

In order for these tests to run in the test suite, without the real instrument
present, some special directives can be added. These allow defining the needed
settings of the instrument to run the test script in simulation mode.

The test scripts have to be located in the `testscripts` subdirectory of each
facility/instrument directory.

The syntax is quite simple. Each line starting with::

   # test: key[ = value,[value]]

will be used as a directive for the tests to configure the NICOS to run the test
script.

There are the following directive:

- ``skip`` - the script shouldn't be executed (for test scripts that are to be
  used only with the live instrument)
- ``subdirs`` - list of directories where setup files should be searched
  (similar to the `setup_subdirs` in the ``nicos.conf`` configuration files)
- ``setups`` - list of setups that should be loaded
- ``setupcode`` - code which has to be executed before the code of the script is
  executed (similar to the ``startupcode`` in the setup files)
- ``needs`` - list of Python modules needed for this test to run, if there is at
  least one missing the testscript will be skipped
- ``timing`` - a condition which may used to limit the time needed for the
  execution code to pass the test or not

Each directive may occur more than once (except for `skip` and `timing`) in the
same file.

Example:

.. literalinclude:: ../../../nicos_mlz/refsans/testscripts/basic.py


Cache entries
^^^^^^^^^^^^^

For some tests some data (device values and/or parameters) need to represent a
valid state of the real instrument, while the dry run in the test suite can only
initialize everything with default values.  Therefore, a way is provided to
inject some of these values into the cache running at test time.  Cache entries
must be written to a file named ``cache`` located in the ``testscripts``
subdirectory of the instrument directory.

Example:

.. literalinclude:: ../../../nicos_mlz/refsans/testscripts/cache
