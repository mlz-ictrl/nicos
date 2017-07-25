User scripts
============

General
-------

The scripting and command language is a slightly restricted Python. In the
following, when talking about scripts we always talk about both commands entered
at the NICOS command prompt and scripts run via the script editor unless
explicitly stated.

Scripts are running inside the NICOS daemon. As many clients are allowed to
connect, all scripts are queued and will run once the next slot is free. If
the daemon is busy while sending an execution request, the clients may offer
to run it immediately, interrupting any running command. Beware that this may
affect a running data collection.

Restrictions
------------

While most Python features are fully supported, there are some restrictions
imposed to keep the system in a sane state:

  * It is  not allowed to overwrite objects in the system namespace.
    This includes device names and commands provided by the system.
  * There is no access to the client side filesystems unless the
    filesystem is shared via e.g. NFS or CIFS.


