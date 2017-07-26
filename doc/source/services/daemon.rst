.. index:: !daemon, !nicos-daemon
.. _daemon:

The NICOS execution daemon
==========================

The NICOS execution daemon (usually just called "NICOS daemon") is the server
part of the client-server execution shell.  It runs NICOS commands and scripts
entered by the user from a client, e.g. the ``nicos-gui`` or ``nicos-client``.

Multiple clients can connect to the same daemon, and an authentication system is
in place to determine which user has which privileges.


Invocation
----------

The daemon is invoked by the ``nicos-daemon`` script.  It should normally be
started by the :ref:`init script <initscript>`.

The daemon expects a setup file with a device named ``Daemon``.

.. The file must be named either ``daemon.py`` or :file:`SETUPNAME.py`, where
   ``SETUPNAME`` is a user-defined name.

On startup using the ``nicos-daemon`` executable, the setup loaded is either
``daemon.py`` if started with no arguments, or ``SETUPNAME.py`` if started
with command line arguments ``-S`` or ``--setup``.

There are several command-line options that allow to customize the startup of
the daemon.

.. program:: daemon

.. option:: -h, --help

    show the help message and exit

.. option:: -d, --daemon

    daemonize the daemon process

.. option:: -S SETUPNAME, --setup=SETUPNAME

    name of the setup, default is 'daemon'


Setup file
----------

The setup file for the daemon is by default:
``<setup_package>/<instrument_name>/setups/special/daemon.py``.

A simple setup file for the daemon could look like this::

  description = 'setup for the execution daemon'
  group = 'special'

  import hashlib

  devices = dict(
      Auth   = device('nicos.services.daemon.auth.ListAuthenticator',
                      hashing = 'sha1',
                      # first entry is the user name, second the hashed password, third the user level
                      passwd = [('guest', '', 'guest'),
                                ('user', hashlib.sha1(b'user').hexdigest(), 'user'),
                                ('admin', hashlib.sha1(b'admin').hexdigest(), 'admin')],
                     ),
      Daemon = device('nicos.services.daemon.NicosDaemon',
                      server = 'localhost',
                      authenticators = ['Auth'],
                     ),
  )

The Daemon device needs to have a ``server`` parameter that specifies the
listening address ``host:port``, in our example ``localhost:1301`` since the
default port is ``1301``.

It also has a list attached devices, the ``authenticators``.  Authenticators
determine if the login name and password presented in clients are accepted by
the daemon, and which user level the user gets.  There are different
:ref:`authenicator classes <authenticator_classes>`.

In our example the password for the user ``guest`` is empty meaning no password
is needed to authenticate.

.. warning::

   The example makes also the other passwords visible to you. This should be
   strictly avoided. You should set the hash values instead of using the
   technique displayed in the setup taken from the Demo instrument.

There are :class:`several other parameters <nicos.services.daemon.NicosDaemon>`
that can be configured, but the standard setting is usually sufficient.

.. _userlevels:

User levels
-----------

There are three user levels: GUEST, USER, and ADMIN.  A higher user level can
stop scripts running started by a lower user level.

.. note::

   The order of the user level is ``GUEST -> USER -> ADMIN`` where GUEST is the
   lowest level.

Also, individual devices and methods can be defined as requiring a certain user
level, see :func:`.requires` and the `.Moveable.requires` parameter.


Daemon class
------------

.. module:: nicos.services.daemon

.. autoclass:: NicosDaemon()

.. note::

   The ``simmode`` parameter is useful if you want to configure two daemon
   instances, one running normally and one running exclusively in simulation mode.
   For this purpose the possibility of multiple daemon setups (see above) also
   comes in handy.

.. _authenticator_classes:

Authenticator classes
---------------------

.. module:: nicos.services.daemon.auth

.. autoclass:: LDAPAuthenticator()

.. autoclass:: ListAuthenticator()

.. autoclass:: PamAuthenticator()
