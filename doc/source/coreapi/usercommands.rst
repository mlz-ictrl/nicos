Writing commands
================

.. module:: nicos.commands

Writing a custom user command is easy: just write a normal function and apply
the `usercommand` decorator.  The docstring of the function is the help for the
command.  A user command should raise `.UsageError` when used improperly: the
command help is shown automatically when such an error is raised.

In order to make user commands available in the NICOS namespace, they must be in
a module that is mentioned by a :ref:`modules list <setup_modules>` in a loaded
setup (see :ref:`setups`).

.. autofunction:: usercommand
