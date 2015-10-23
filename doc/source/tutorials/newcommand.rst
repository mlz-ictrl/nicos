.. _create-new-command:

Creating a new command
----------------------

Creating a new custom user command is easy: just write a normal function and
apply the `~nicos.commands.usercommand` decorator::

   @usercommand
   def mycommand(...):
      ...

The docstring of the function is the help for the command and should include a
usage example.  A user command should raise `~nicos.core.errors.UsageError` when
used improperly: the command help is shown automatically when such an error is
raised.

Another very useful decorator is `~nicos.commands.helparglist`.  It gives hints
to the user what parameters for the command are expected in the online help
system.  The default is to show the argument list as in Python, which is fine for
simple argument lists but can be too confusing or distract from the intended
usage for complex commands.  Example::

   @usercommand
   @helparglist('dev, ...')
   def mycommand(*devs):
      ...

The command name itself has to be added into the module's ``__all__`` list.  So
at the top of the module you should have ::

   __all__ = [..., 'mycommand', ...]

In order to make user commands available in the NICOS namespace, they must be in
a module that is mentioned by a :ref:`modules list <setup-modules>` in a loaded
setup (see :ref:`setups`).  If the ``mycommand`` is defined in the module
``path.to.mycommands`` it will be accessable via::

   modules = ['path.to.mycommands', ... ]

where the **path.to** is the proper module path.
