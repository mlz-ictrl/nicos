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

There are no special command-line arguments.  The daemon expects a setup file
with a device named ``Daemon``.  The file must be named either ``daemon.py`` or
:file:`daemon-{name}.py`, where ``name`` is a user-defined name.  On startup
using the ``nicos-daemon`` executable, the setup loaded is either ``daemon.py``
if started with no arguments, or ``daemon-name.py`` if started with argument
``name``.


Setup file
----------

A simple setup file for the daemon could look like this::

  description = 'setup for the execution daemon'
  group = 'special'

  import hashlib

  devices = dict(
      Auth   = device('services.daemon.auth.ListAuthenticator',
                      hashing = 'sha1',
                      # first entry is the user name, second the hashed password, third the user level
                      passwd = [('guest', '', 'guest'),
                                ('user', hashlib.sha1('user').hexdigest(), 'user'),
                                ('admin', hashlib.sha1('admin').hexdigest(), 'admin')],
                     ),
      Daemon = device('services.daemon.NicosDaemon',
                      server = 'localhost',
                      authenticators = ['Auth'],
                     ),
  )

The Daemon device needs to have a ``server`` parameter that specifies the
listening address ``host:port`` (the default port being 1301).

It also has a list attached devices, the ``authenticators``.  Authenticators
determine if the login name and password presented in clients are accepted by
the daemon, and which user level the user gets.


.. _userlevels:

User levels
-----------

There are three user levels: GUEST, USER, and ADMIN.  A higher user level can
stop scripts running started by a lower user level.

Also, individual devices and methods can be defined as requiring a certain user
level, see :func:`.requires` and the `.Moveable.requires` parameter.


Authenticator classes
---------------------

.. module:: nicos.services.daemon.auth

.. autoclass:: ListAuthenticator()

.. autoclass:: PamAuthenticator()
