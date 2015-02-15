.. _gui-designer:

Using the Qt designer with NICOS widgets
========================================

For easy programming of graphical interfaces, NICOS provides a couple of
Qt widgets that can display and edit information about NICOS devices or
device parameters.

NICOS provides the ``bin/designer-nicos`` script that starts the Qt designer
with appropriate options to add the widgets to the designer's of widgets
(see below for custom widgets).

The ``bin/designer-nicos`` script should be invoked to start the Qt designer
with NICOS widgets integrated.  If custom widgets should be included, give
the module name(s) with widget classes on the command line.  For example, ::

   bin/designer-nicos nicos.sans1.monitorwidgets custom/sans1/gui/panel.ui

will edit the ``panel.ui`` file with the widgets from
``nicos.sans1.monitorwidgets`` available in addition to the standard widgets
mentioned above.
