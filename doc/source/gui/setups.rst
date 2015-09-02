.. _gui-config-setup:

Setup depending configuration
=============================

For some reason it would be nice to display some elements in the GUI or status
monitor only in case of some loaded or not loaded setups.

To solve this problem you may use the ``setups`` option which could given for the
:func:`panel` entries in the GUI configuration files as well as for the
:func:`Block` entries in the status monitor configuration files.

The syntax of the setups is the following:

 * names of the setups as a string
 * an exclamation mark ``!`` or a ``not`` in front of the setup name inverts the
   meaning
 * setup names could be combined with the keywords ``and`` and ``or``.
 * as wildcard an asterisk ``*`` is used.
 * brackets may be used to group the experessions

If a simple name is given the setup condition is fulfilled if the setup is loaded
in the NICOS :term:`master`.  Otherwise you can use Python boolean operators and
parentheses to construct an expression like ``(setup1 and not setup2) or setup3``

To match multiple setups, use filename patterns, for example: ``ccr* and not cryo*``.

Examples:
---------

 * 'biofurnace' - gives True if this setup is loaded, otherwise False
 * '!biofurnace' - gives False if this setup is loaded, otherwise True
 * 'ccr*' - gives True if any setup is loaded which name starts with 'ccr',
   otherwise False
 * '!ccr*' - gives False if any setup is loaded which name starts start with 'ccr',
   otherwise True
 * ['biofurnace', '!ccr*'], 'biofurnace and !ccr*', 'biofurnace and not ccr*' - these
   notations are equivalent and give True if the 'biofurnace' setup is loaded
   but not any starting with 'ccr', otherwise False
 * 'biofurnace and not ccr01' - gives True if the 'biofurnace' setup is loaded but
   not the 'ccr01' setup, otherwise False
 * '(biofurnace and not (ccr01 or htf01)' - gives True if the 'biofurnace' setup
   is loaded but not any of 'ccr01' or 'htf01', otherwise False

