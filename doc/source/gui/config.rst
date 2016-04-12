.. _gui-config:

GUI configuration
=================

The layout of the GUI client can be configured very extensively with the help of
a configuration file usually called ``custom/<instrument>/guiconfig.py`` (another
such file can be selected at startup with the ``-c`` option).

The configuration file is a Python module that uses several special functions
that together describe the lay-out of Qt panels and windows.

.. _gui-config-example:

A small example configuration file looks like this:

.. code-block:: python
   :linenos:

   main_window = docked(
       vsplit(
           panel('status.ScriptStatusPanel'),
           panel('console.ConsolePanel'),
       ),
       ('NICOS devices', panel('devices.DevicesPanel', icons=True, dockpos='right',))
   )

   windows = [
       window('Editor', 'editor',
           vsplit(
               panel('scriptbuilder.CommandsPanel'),
               panel('editor.EditorPanel'),
           )
       ),
       window('Scans', 'plotter', panel('scans.ScansPanel')),
   ]

   tools = [
       tool('Calculator', 'calculator.CalculatorTool'),
       tool('Report NICOS bug', 'website.WebsiteTool',
            url='http://forge.frm2.tum.de/redmine/projects/nicos/issues/new'),
   ]

There must be three top-level values called ``main_window``, ``windows`` and
``tools``.

``main_window`` is the panel configuration for the main window, the other window
configurations must be created by ``window()`` and contain panel configurations
for auxiliary windows that can be opened from the GUI's toolbar and "Windows"
menu.

The ``tools`` entry specifies a list of tools that can be run from the GUI's
"Tools" menu.  They should be small, short-lived dialogs that typically do not
stay open for very long.

Panel combinators
-----------------

The basic building blocks for windows (main and auxiliary) are :ref:`panels<panels>`.
Windows can consist of single panels, or multiple panels combined in several
ways.

The functions to combine several panels are:

.. function:: docked(main, *rest)

   Creates a main panel, with several docks.  The first argument is the main
   panel (or another combination of panels), while the rest of the arguments are
   tuples of ``(dockname, panelconf)``, as in the example config above.

   This must be the toplevel element for a window, it should not be a child
   element.

.. function:: tabbed(*tabs)

   Creates a tab widget (with tabs that can be reordered and dragged out of the
   widget as separate windows).  The arguments are tuples of ``(tabname,
   panelconf)``.  This can be used as the "main" element of a ``docked``
   configuration.

.. function:: hsplit(*confs, **options)

   Creates a layout of panel configurations separated horizontally by splitters.

   Options:

   * The ``setups`` options gives the possibility to define a setup depending
     display of the panels, see :ref:`gui-config-setup`

.. function:: vsplit(*confs, **options)

   Creates a layout of panel configurations separated vertically by splitters.

   Options:

   * The ``setups`` options gives the possibility to define a setup depending
     display of the panels, see :ref:`gui-config-setup`


.. _gui-config-setup:

Setup depending configuration
-----------------------------

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
^^^^^^^^^

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

.. _panels:

Panels
------

The function to create a single panel is:

.. function:: panel(classname, **options)

   This creates a single panel of class ``classname``.  The class name must be
   fully qualified with the module name to import it from, with the exception
   that if it begins with ``nicos.clients.gui.panels.`` that can be left out.

   See :ref:`the example config above <gui-config-example>`.

   Options:

   * The ``setups`` options gives the possibility to define a setup depending
     display of the panels, see :ref:`gui-config-setup`

   * The ``dockpos`` options is only used if the panel is part of the
     :func:`docked` panel and give the default position insight a dock widget.

     The values could be:
        - left
        - right
        - top
        - bottom

   The other possible ``options`` are panel-specific; the keywords given here
   are passed to the panel.

Each panel is implemented by a class inheriting from
``nicos.clients.gui.panels.Panel`` and usually a Designer ``.ui`` file.  See
:ref:`gui-panels` for a description of the panel interface.

Panels can provide menus and toolbars; these are all collected by the window
they are displayed in.

Panels that come with NICOS are:

``console.ConsolePanel``
   Provides a console-like interface where commands can be entered and the
   output from the NICOS daemon is displayed.

   Options:

   * ``hasinput`` (default True) -- if set to False, the input box is hidden and
     the console is just an output view.
   * ``hasmenu`` (default True) -- if set to False, the console does not provide
     its menu (containing actions for the output view such as Save or Print).

.. figure:: consolepanel.png
     :alt: console panel
     :align: center

``commandline.CommandLinePanel``
   Provides just an input box for entering commands and no output view.

.. figure:: commandlinepanel.png
     :alt: command line panel
     :align: center

.. _commandbuilder-commandpanel:

``cmdbuilder.CommandPanel``
   Provides a panel where the user can click-and-choose a NICOS command with the
   help of GUI elements known as "cmdlets".

   Options:

   * ``modules`` (default [ ]) -- TODO

.. figure:: commandbuilder.png
     :alt: command panel
     :align: center

``devices.DevicesPanel``
   Provides a graphical list of NICOS devices and their current values.  The
   user can operate basic device functions (move, stop, reset) by selecting an
   item from the list, which opens a control dialog.

   Options:

   * ``useicons`` (default True) -- if set to False, the list widget does not
     display status icons for the devices.

.. figure:: devicepanel.png
     :alt: device panel
     :align: center

``editor.EditorPanel``
   Provides a text editor specialized for entering scripts, together with
   actions such as Run or Simulate.  The editor widget is QScintilla if it is
   installed, and a standard text edit box otherwise.

.. figure:: editorpanel.png
     :alt: editor panel
     :align: center

``elog.ELogPanel``
   Provides a HTML widget for the electronic logbook.

.. figure:: elogpanel.png
     :alt: electronic logbook panel
     :align: center

``errors.ErrorPanel``
   Provides an output view similar to the ConsolePanel, but that only displays
   messages with the WARNING and ERROR loglevel.

.. figure:: errorpanel.png
     :alt: error panel
     :align: center

``expinfo.ExpInfoPanel``
   Provides a panel with several labels that display basic information about the
   current experiment, such as experiment title, sample name and user name.

   It also provides several buttons with which the user can change proposal
   info, sample properties, scan environment and setups.

   Options:

   * ``sample_panel`` -- what to show when the user clicks on the "Sample"
     button.  The value must be a panel configuration, e.g. ``panel('...')`` or
     ``tabbed(...)``.

     There are several panels that are useful for this:

     - ``nicos.clients.gui.panels.setup_panel.GenericSamplePanel`` -- a panel
       that only shows a single input box for the sample name.
     - ``nicos.clients.gui.panels.setup_panel.TasSamplePanel`` -- a panel that
       also shows input boxes for triple-axis sample properties (such as lattice
       constants).

.. figure:: experimentinfopanel.png
     :alt: experiment info panel
     :align: center

``history.HistoryPanel``
   Provides a panel where the user can create time series plots of any cache
   values.

.. figure:: historypanel.png
     :alt: history panel
     :align: center

``live.LivePanel``
   Provides a generic "detector live view" for 2-D images.  For most
   instruments, a specific panel must be implemented that takes care of the
   individual live display needs.

   Options:

   * ``instrument`` -- the instrument name that is passed on to the livewidget
     module.

.. figure:: livewidgetpanel.png
     :scale: 75%
     :alt: livewidget panel
     :align: center

``logviewer.LogViewerPanel``
   Provides a possibility to view various NICOS log files.

.. figure:: logviewerpanel.png
     :alt: log viewer panel
     :align: center

``scans.ScansPanel``
   Provides a display for the scans of the current experiment.

.. figure:: scanspanel.png
     :alt: scans panel
     :align: center

``scriptbuilder.CommandsPanel``
   Provides a panel where the user can click-and-choose multiple NICOS commands
   with cmdlets (similar to the
   :ref:`cmdbuilder.CommandPanel <commandbuilder-commandpanel>` but for multiple
   commands).

   Options:

   * ``modules`` (default [ ]) -- TODO

.. figure:: scriptbuilderpanel.png
     :alt: script builder panel
     :align: center

``status.ScriptStatusPanel``
   Provides a view of the currently executed script, and the current position in
   it.  The panel also displays queued scripts.

   Options:

   * ``stopcounting`` (default False) -- Configure the stop button behaviour,
     if is set to ``True``, the execution of a script will be aborted, otherwise
     a counting will be finished first before the script will be stopped.

.. figure:: scriptstatuspanel.png
     :alt: script status panel
     :align: center

``watch.WatchPanel``
   Provides a way to enter "watch expressions" similar to a debugger and
   evaluate them regularly.

.. figure:: watchpanel.png
     :alt: console panel
     :align: center

``generic.GenericPanel``
   Provides a generic implementation of Panel that can display any ``.ui`` file
   using NICOS GUI widgets (see :ref:`gui-widgets`).

   Options:

   * ``uifile`` -- the path to the UI file to display

.. figure:: genericpanel.png
     :alt: generic panel
     :align: center


Auxiliary windows
-----------------

.. function:: window(name, icon, panelconf)

   This represents an auxiliary window.  ``name`` is the label for the window
   (and the action that opens it) and ``icon`` the name of an icon in the NICOS
   Qt resources to use for the action that opens the window.

   ``panelconf`` is the panel configuration for that window.


Tools
-----

.. function:: tool(name, classname, **options)

   This represents a tool window.  ``name`` is the label for the menu entry that
   starts the tool.

   ``classname`` must be the fully qualified name of a QDialog subclass that is
   displayed as the tool.  As for panels, ``nicos.clients.gui.tools.`` can be
   left out of the name if it starts with that.

   ``options`` are passed to the tool as for panels.

.. function:: cmdtool(name, cmdline)

   This represents an external tool that is started with a system command.
   ``name`` is the menu entry label.

   ``cmdline`` is a list of the executable and command-line arguments, e.g.
   ``['quango', '-n', 'somehost']``.

.. function:: menu(name, *subitems)

   Represents a tool sub-menu.  The ``subitems`` are again ``tool``, ``cmdtool``
   or ``menu`` items.


Tools that come with NICOS are:

``calculator.CalculatorTool``
   A dialog with several tabs for several neutron-related calculations (elastic
   scattering, conversion between wavelength and energy etc.)

.. figure:: calculatortool.png
     :alt: calculator tool
     :align: center

``commands.CommandsTool``
   A dialog that displays a list of buttons that start shell commands.  This can
   be used for maintenance commands that the user should be able to start
   without knowing the command.

   Options:

   * ``commands`` -- a list of tuples ``(text, shellcommand)``.  For each of
     them a button is created in the dialog.

.. figure:: commandstool.png
     :alt: commands tool
     :align: center

``estop.EmergencyStopTool``
   A small window with a big "emergency stop" button that stays on top of other
   windows, and when clicked triggers an "immediate stop" action in NICOS.

.. figure:: emergencystoptool.png
     :alt: emergency stop tool
     :align: center

``website.WebsiteTool``
   A dialog that just displays a website using the Qt HTML view.

   Options:

   * ``url`` -- the URL of the web site.

.. figure:: websitetool.png
     :scale: 50%
     :alt: website tool
     :align: center
