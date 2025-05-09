Changelog
=========

Release 3.12.0
--------------

* Core

  - Dropped support for TACO devices.

  - New parameter types/validators ``nonzero`` and ``secret``.

  - Scripts can now be stopped while waiting for devices to move.

  - Refactored the device polling interface.

  - Improved documentation of ``usermethod``\ s, which is displayed in the
    help window.

  - Added new elog event to hide/show events.

  - NICOS now notifies the user regularly when a script is still paused.

* Commands

  - Argumentless ``stop()`` now tries to list the devices that were
    actually stopped.

  - Added the ``userinput`` command to request input interactively.

  - Dropped support of the "Simple Parameter Mode".

  - Refactored interface of Q scan related commands to allow more user friendly
    parameter formats.

  - Added ``HideLog`` command to temporarily hide content by default in the
    electronic log.

  - ``SetMode`` is not a visible user command anymore.

  - ``waitfor_stable`` is now a common command.

  - The ``help`` command now allows the ``usermethod``\ s of a device as
    parameters.

* GUI

  - Enable a configurable connection dialog.

  - Moved the ``tomo`` command cmdlet into a separate file to remove it as
    standard cmdlet.

  - Added a ``center`` command cmdlet.

  - Added a ``waitfor`` and ``waitfor_stable`` command cmdlet.

  - Removed the ``ScanTool`` tool (substituted by scan cmdlets).

  - Help windows shows device ``usermethod``\ s.

  - The pause/stop buttons now always show the dropdown menu to select
    which pause/stop mode is appropriate for the situation.

* Services

  - Dropped the ``pushversioninfo`` service.

* Documentation

  - Added elog messages format and data description.


Release 3.11.0
--------------

* Core

  - NICOS now requires at least Python 3.9 to run.

  - The InfluxDB cache backend now is faster and correctly handles last values
    and history queries for periods without value changes.

* Commands

  - ``floatrange`` renamed to ``FloatRange`` for consistency.

* Devices

  - Gap devices can now allow blades to overlap or keep a minimum opening with
    the new ``min_opening`` parameter.

  - Support adapting the simulated neutrons to different hosts in McStas
    devices.

  - Added integration for the RabbitMQ data catalog pipeline and eWorkbench
    electronic logbook backend.

  - Added options to filter and wrap NICOS devices when connecting to a SEC node
    and automatically creating devices for each module.

  - Added mail notifier that automatically includes the hostname in the subject.

* GUI

  - Readonly parameter values can now be copied from the GUI device "details"
    dialog.

  - Selected parts of console output can be added to the electronic logbook.

  - Added more file readers to reopen already measured data files.

  - Use better default colors for scan/history plot curves.

  - Initial support for dark-mode system UI themes.

* Other

  - The electronic logbook can now have multiple backend handlers.

  - Increased test coverage and added tests for selected GUI components.

  - Added many more test scripts for individual instruments.


Release 3.10.0
--------------

* Core

  - Added an experimental InfluxDB backend for the NICOS cache.

  - The cache supports prefiltering history by a minimum time interval, speeding
    up query execution.

  - The ``lowlevel`` parameter is replaced by finer-grained ``visibility``.

* Commands

  - Use of ``time.sleep`` is now warned about, users should use NICOS' ``sleep``
    instead.

* Devices

  - Added a general slit based on two-bladed gap devices.

  - Added a method to query the preset on the generic detector.

  - The SECoP integration has been updated, and the ``frappy`` package is now
    not required on the client side.

  - On classes inheriting from Device, it is now a hard error to set attributes
    with names not starting with ``_``, except if they are NICOS parameters.

  - Data sink devices are now hidden from the user by default.

  - The order of calling data sink handlers can now be configured by a new
    class attribute.

* GUI

  - Device targets are now displayed in a new column in the devices panel.

  - The SSH tunnel option can now be configured in the GUI.

  - Large scan metadata will not be transferred to the GUI anymore, speeding
    up transfer of datasets.

  - The point number can now be used as an X-axis in scan plots.

  - The scan plot should now use the same color series for each new graph,
    making them easier to compare.

  - Building installer packages for macOS is now supported.  Packages will be
    available on `our website <https://nicos-controls.org/download>`_.

  - Qt 6 is now supported.  At the moment, support is experimental and needs to
    be activated using the environment variable setting ``NICOS_QT=6``.

  - "Measure" type commandlets can now specify arbitrary presets, not only time.

  - The guiconfig can now specify default connection presets for the GUI client
    as an additional option.

* Other

  - A ``/pause`` meta-command has been added to the CLI client.

  - For watchdog conditions, a "precondition cooldown" time can now be
    configured.

  - Additional help topics can be added to each setup, and they will be
    displayed in the GUI/CLI help section for the setup.

  - The LDAP authenticator can now query multiple LDAP servers.

  - The email notifier can now connect to an SMTP server requiring login.

  - The electronic logbook daemon can now be configured to use multiple backend
    handlers at the same time.


Release 3.9.0
-------------

* Core

  - ``nicos.conf`` files are now in TOML format.  The ``toml`` library is a new
    dependency.

  - Added general NeXuS support (taken from SINQ implementation).

  - The ``lowlevel`` device parameter has been replaced by a new parameter
    ``visibility``, which can specify the visibility for different categories,
    e.g. the user namespace or the measurement metadata.

  - A new mixin ``HasAutoDevices`` can be used to consistently handle
    auto-subdevices and their properties.

* Commands

  - Added ``stddev`` statistics function for the environment to record the
    standard deviation of a device's value during acquisition.

  - Added the ``ListUsers`` command.

  - Added the ``ListDatasinks`` command.

* Devices

  - Added a generic "calculated readable" device that combines the values of two
    other devices.

  - The Epics integration now supports different protocols via the ``caproto``
    and ``p4p`` libraries.

  - The Tango devices depending on the MLZ interface specification have been
    moved to ``nicos.devices.entangle``.

  - The McStas support for virtual devices has been extended to cover single
    detectors/counters and now includes a separate device to configure
    parameters related to McStas.

* GUI

  - NICOS Scan files can now be re-read and displayed in the scan window.

  - The key expressions for history plots (and monitor widgets) can now
    be any Python expression involving key names, e.g. ``(cryo + 5) * 3`` or
    ``sin(motor)**2``.

  - The dry results can't be collapsed anymore but closed.

  - Display 3D data by summing in z direction as 2D pictures in live
    data panel.

  - Added interface to initialize control elements in live data panel.

  - Live plot images can now be easily added to the elog.

  - Expert mode can now be pre-set in a connection profile.

  - The live data window can now use colormaps from the ``colorcet`` library, as
    well as custom ones defined by the user.

* Other

  - A new IPython client interface has been added.  See ``doc/iPython.rst`` for
    usage and details.

* Docs

  - Updated and expanded the "set up a new instrument" howto guide.


Release 3.8.0
-------------

* Core

  - NICOS now requires Python 3.6 to run.

  - All files produced by or delivered with NICOS will be encoded as UTF-8.

  - The live data transport protocol has been extended, so that 1-D data
    can be delivered with information about the abscissa labels, and
    multiple data curves can be sent in a single event.

  - The SECoP (https://github.com/SampleEnvironment/SECoP) integration has
    been improved.

  - McStas support has been improved and extended.

  - Cleaned up the proposal management in the Experiment class.

  - Added a notifier class for `Mattermost <https://mattermost.com/>`_.

  - Tracebacks in logfiles and shown to the user now support Python 3 chained
    exceptions.

* Commands

  - Added ``gridscan``, which performs a scan over an orthogonal grid of
    multiple devices.

* GUI

  - The GUI now requires PyQt 5.

  - Devices that fail to create are now shown in the devices list with an error
    symbol, instead of being omitted from the list entirely.

  - Add editor config to pop out dry run windows.  This makes sense when the
    editor is in a panel configuration with limited vertical space, e.g. with a
    script builder on top.

  - Live data view changes:
    Add capability to display more than 1 curve in the live data view panel.
    Add configuration to select the displayed data file types, marker types,
    and line types. Additionally added some configuration to define the default
    behaviour for new live data.

  - Plots can now be exported as graphics from the history viewer.

  - Improved Windows client building.

  - Many more image data formats can now be read back in from file in the Live
    Data panel.

  - ``.desktop`` files are now provided for ``nicos-gui`` and ``nicos-history``
    to add NICOS to the application menu on Linux.

  - The electronic logbook now accepts Markdown formatted text entry.

* Watchdog

  - Reduced the chattering if only the message changes but not the level.

  - Added timeout parameter for each entry.

* Documentation

  - Added data handling description and tutorial how to check the setup files.


Release 3.7.0
-------------

* Core

  - The handling of detector presets has been changed: preset names (other than
    time) now primarily come from device names.  For example, "mon1=1000" can
    only be used as a preset if there is a monitor channel called "mon1" in
    the detector.  Exceptions are possible, but must be configured.

  - Any detector channel can now be used as a preset.  For channels which don't
    have the ability to stop the measurement at the hardware level, NICOS will
    check that the preset is reached and stop in software.  This allows, for
    example, measuring until a certain number of counts in a region of interest
    is reached.

  - The "lttb" module has been unbundled and is now an external requirement.

* GUI

  - Qt 5 is now preferred if installed, and Qt 4 can be forced by setting
    "NICOS_QT=4" in the environment.

  - A new panel has been added that allows run-time reconfiguration of which
    watchdog conditions should be enabled.  Resolved warnings are now shown as
    such in the notification window.

* Commands

  - Added new core commands "rmove()" and "rmaw()" for relative movement
    of devices.

  - The "help()" command can now be called with a string that represents
    a command or device and will show the correct info.

  - "appendscan()" now works for scans over multiple devices.

* Devices

  - Support for accessing SECoP (Sample Environment Control Protocol) nodes as
    NICOS devices has been added.

  - QMesyDAQ devices with Tango interface have been added.

  - Optional Slack notifier is not longer Python 2 compatible.

* Watchdog

  - The watchdog daemon has been rewritten.  Conditions can now be defined in
    individual setups, together with the devices they relate to.

* Status Monitor

  - Status monitor "block" elements can now be defined in individual setups,
    together with the devices they relate to.  This makes the creation of
    status displays for common sample environments much easier.


Release 3.6.0
-------------

* Core

  - In data acquisition, detector prepare() is now called after setPreset().

  - The command-line client can now display subsecond timestamps.

  - Experiments can now force single count()s to produce a scan dataset
    with one point.

  - A device parameter can now be defined as "internal", which means that it is
    managed exclusively by the device's code, and not accepted in setup files.

  - Non-Readable devices now also have an "active in dry-run" flag.

  - The new parameter validator "oneofdict_or" allows naming some special
    device values while also supporting unnamed values inbetween.

  - The collector daemon can now map device keys when forwarding between caches.

  - Added a Lorentzian fitter for use in the GUI and fit commands.

  - Daemon user authenticators can now add metadata to the returned User
    objects.

* GUI

  - The display of the executed script now includes line numbers.

  - The device panel shows more actions for non-moveable devices, such as
    reset and enable/disable.

  - A new panel is available for low-level access to PLC devices following
    the PILS specification.

  - The Qt monitor now supports scale/offset specifiers for plotted values.

  - The standalone history application now also supports saved presets,
    restoring views, and listing the available keys for display, and it allows
    choosing the cache server to use.

  - Tabs in a tab bar guiconfig element can now be displayed on the left side.

* Devices

  - Added a debugging data sink.

  - Added a Tango MotorAxis device.

  - Added a device to receive instructions from a barcode reader.

  - Slit devices can now reference their axes in parallel.

* Commands

  - Added "abort()" which stops a script from within the script,
    which is more intuitive than raising an exception.

* Tools

  - Added systemd integration with a unit that generates and starts units for
    each configured NICOS service, similar to the init script.

  - Added a tool to generate password hashes for the daemon setup.

  - Added a tool to rename devices in a flatfile cache database.

* Development

  - Many more fixes for Python 3 and Qt 5.


Release 3.5.0
-------------

* Core

  - Setups with group 'configdata' will now be handled like normal setups. This
    allows to access to the values from any other setup file.

  - The 'tupleof' parameter type now accepts numpy arrays.

  - The 'ParamDevice' can now return the status of the referenced device.

  - Improved 'Dry run' mode by fixing some issues like calling 'doVersion' and
    (for TACO devices) 'doUpdate*' methods and using the hardware stubs for
    TACO/TANGO/EPICS devices.

  - Breakpoints now work as expected in the daemon debugger.

* GUI

  - Improved compatibility with Qt 5.

  - Created a nicer 'About' dialog and removed the 'About Qt' dialog.

  - The scan plot now tries harder to select a proper X-axis by determining
    the first changing device.

  - Show value labels for for multi-value devices in device dialogs.

* Commands

  - The 'tomo' command now accepts additional detectors.

* Watchdog

  - Conditions learned the full setup dependency syntax like the status monitor
    fields and groups.

* Tests

  - Instrument specific test scripts are now run during the test suite, in
    dry-run mode.

* Development

  - All modules now using several future imports for Python 3 compatibility.

  - Import order has been made consistent using 'isort'.


Release 3.4.0
-------------

* New client/server protocol(s)

  - The daemon communication layer has been made protocol independent. It is
    now possible to configure the transport layer and serializer to allow
    connections from clients which are not running in the Python world, without
    implementing the Python pickle protocol on the client side.

* Core

  - Added support for disabling devices.  The components here are a new
    'CanDisable' mixin, a new status 'DISABLED' to show disabled devices,
    and new GUI elements to disable/reenable the devices.

  - The compatibility of new setups will be checked *before* starting to
    unload/load anything, so the user will not get an empty device list in case
    of an error during loading a new setup.

  - Attached devices can now be allowed to not exist in the loaded
    configuration.

  - Userlimits are reinitialized when set to (0, 0).

  - 'Multi' methods (multiWait, multiStatus, ...) now raise the highest-
    severity exception. Repeated display of exceptions when waiting on a
    single device is avoided.

  - Runtime re-assignment of device methods is now forbidden.

  - Current script name is now returned in the daemon "getstatus" query.

* GUI

  - Implemented log-x scale for scan plotting.

  - Added an option to show/hide error bars in scan plots.

  - The window entries in the GUI config learned the 'setups' option to display
    them depending on the loaded setups in daemon.

  - The "control device" dialog now hides the device parameters at first, but
    allows to display them. In 'expert mode' they will be displayed by default.

* Commands

  - tomo: add a parameter to rearrange the 180 deg position into the sequence
    of the positions instead beeing the first position.

  - Improved cosine fit.

* Dry-run

  - Full log output is now available even in sandbox mode.

  - Fixed TACO/TANGO/EPICS devices access.

  - Fixed Measurables with hardware access.

  - SeqSleep is now not executed anymore.

* Tools

  - check_setups: 'Exp' device is now allowed in more than one setup.

* Tests

  - Added timeout decorator to test functions that seem to hang sporadically.

  - Do not try to import special/hidden dirs.

* Doc

  - Added tutorials to create new devices, commands, and data sinks.

  - Added options description of some panels.

* Development

  - All includes are now sorted according to PEP8 rules (but facility
    import follow nicos core imports).


Release 3.3.0
-------------

* Core

  - Added commands "ListMailReceivers" and "ListDataReceivers".

  - A longstanding bug with client connections not closing properly has
    been fixed, it resulted in clients receiving events (like script
    output) multiple times.

  - A "doAdjust" method has been added to customize the action of
    "adjust" and the "offset" parameter to different conventions.

  - The "_Restart" command is now blocked if there are active background
    threads.

* Devices

  - Access restrictions with the "requires" parameter are now checked
    when trying to set device parameters.

  - Notifier devices can now be marked as "private", which means that their
    receivers are not overwritten with the users' addresses for each new
    experiment.

  - Unit handling of several Tango device classes has been improved.

* GUI

  - Rebinning of very large history datasets has been changed to use a
    "triangular downsampling" algorithm that better preserves interesting
    features of the data in question.

  - Triangular downsampling also applies to status monitor plots.


Release 3.2.0
-------------

* Core

  - The "center()" and "checkoffset()" commands can now use any defined
    fitting function, or "center_of_mass", to determine the peak center.

  - Fitting commands output the relative error as a column.

  - The collector service can now forward cache values to multiple different
    backends (NICOS cache/webhooks).

* Devices

  - Tango VectorInput/VectorOutput are now supported.

  - Added a device to read out the absolute Q value for TAS instruments.

  - The generic detector can now calculate post-processed values from
    scalar-valued PassiveChannels.

  - Added an image sink for writing multiple arrays from a single detector.

* GUI

  - Each setup can now name a "representative" device to show in the
    device tree when the setup is collapsed.

  - The history panel can now save multiple displayed curves in one data file.

  - The selection of a fit function, and whether to pick initial fit points,
    has been reworked in the scans and history panels.

  - All available fit functions can be used in the scans and history panels.

  - Fitting by default uses the currently viewed range to limit the fit range.

  - Custom function presets can be added to the "Fit arbitrary function" dialog
    in the GUI config.

  - Instrument configurations can now include custom dialogs to show on
    NewExperiment and FinishExperiment (if triggered through the proposal
    window).

  - Some minor visual enhancements in the plot displays.

* Demo

  - The "nicos-demo" command now always starts with the demo instrument.
    To use an instrument selected by nicos.conf or the INSTRUMENT environment
    variable, pass the "-O" option.


Release 3.1.0
-------------

* Core

  - The poller now doesn't completely give up when a setup file has syntax
    errors.  Instead, it tries to restart after each file change.

  - The HTML monitor now uses GR instead of Matplotlib for plotting.

  - Added a Kafka backend for the cache server.

  - "Exec now" commands are now executed in the context of the calling client,
    not a generic "system" user.

* GUI

  - Qt 5 is now supported by the GUI application.  Set ``NICOS_QT=5`` to enable
    if PyQt5 is installed on the system.  In later versions, this will become
    the default mode.

  - Support for Qwt as plotting backend has been removed.

  - Added a SSH tunnel option to the client, available with the ``-t`` option.

  - The GR live widget now supports one-dimensional data and multiple live channels.

  - All curves in a history plot can now be saved to data files at the same
    time.

  - Offset and scale in history plots is now applied to string values mapped
    to integers.

  - All scan columns can now be plotted as Y values in scan plots.

  - The setup panel now shows a hint if some setups are not offered for
    loading because of errors.

* Devices

  - Added a generic "pulse" device (that switches an attached device to a
    different value for a selected time).

  - Tango device creation now fails faster if the Tango host is down.

  - Added a notifier class for Slack.

  - The limit handling in the generic Axis class has been overhauled to
    better take the motor's limits into account.


Release 3.0.0
-------------

In this release, the "custom" directory with setups and modules for instruments
has been replaced by Python packages.  The most important consequences from this
change are:

* Individual instrument customizations are separated by facility, called
  ``nicos_<facility>``.  By default, all such packages are installed alongside
  with the main ``nicos`` package.

* Custom modules no longer need to be mapped into ``nicos.<instrument>`` with a
  nonstandard manipulation of ``__path__``, which makes it much easier for tools
  and IDEs to find and process them.

* All device and class names in setups, as well as ``guiconfig.py``, must now
  be fully qualified.  There are no shortcuts (leave out ``nicos.``) anymore.

* The ``custom_paths`` setting for ``nicos.conf`` has been replaced with a
  setting ``setup_package``.  It specifies only a Python package name.  The
  package is found along ``PYTHONPATH``.

* The ``INSTRUMENT`` environment variable should now be of the form
  ``nicos_<facility>.<instrument>``.

Other changes:

* GUI

  - The GR-based live detector view can show ROIs.

  - The device list can now show arbitrary parameters of a device, in addition
    to the current value and status.  Which devices should show which parameters
    is configured in the ``guiconfig.py`` for each instrument.

  - In the scans panel, opening new scans automatically can now be switched off.

  - If a script exits with an error, the last executed line is marked with a
    red arrow in the script view.

  - Multiple bugs have been fixed in the find/replace dialog of the script
    editor.

* Devices

  - A new sequence item, ``SeqWait``, has been added for sequencer devices.

  - EPICS support has been improved considerably.

  - A ``ScanningDetector`` has been added to the generic devices.  On count, it
    will perform a scan of a device and collect the subscan results.

* Commands

  - A new ``waitfor`` command has been added to replace simple while-loops.

* Core

  - The ``rsa`` module is now a required dependency, and will always be used
    for encrypting credentials between the daemon and its clients.

  - Support has been added for encrypted password and other credentials storage.

  - Daemon slowdown due to slow/hanging/intermittent network connections has
    been reduced.

* Documentation

  - The user documentation for some commands was extended.

* Test suite

  - Many tests have been added, and the test suite is more reliable due to a
    rework of test fixtures.

  - Tests can be run in Docker containers.


Release 2.12.0
--------------

* Core

  - Change in daemon protocol: Requests now use an id to allow for reordering
    the requests.

  - New sandboxing mode for simulation mode. This uses an external binary (needs
    to be setuid root) that will call the unshare() system call, which gives the
    process to create a new mount and network namespace.  That allows remounting
    the filesystem read-only in a chroot, and complete isolation of any network
    ports that might be used.

  - Alias config handling is now more useful: when loading setups that do not
    have new selections for existing alias devices, the alias assignments are
    not changed.

  - A new command "pause()" is available to ask for user confirmation via GUI
    before continuing with the script.

  - The watchdog can now emit a message and/or execute an action when a
    warning condition has gone back to normal.

  - The electronic logbook now also saves a plain-text version of the console
    output, which is very similar to the ``nicos-*.log`` files, but saved in
    the user's proposal directory.

  - Added "virtual" goniometers for TAS mode that tilt the sample along the
    sample's orientation reflections, regardless of the physical offset.

* GUI

  - A new livewidget for 2D-images based on gr is available.

  - Allow switchable wrapping in console output.

  - Added "ETA" (estimated finishing time) display to script status panel, which
    uses the simulation mode to get an estimate and update it when individual
    commands are finished.  Care should be taken to only enable this if
    sandboxing is available as well.

  - Device parameters can now be refreshed from hardware on demand (right click
    into the parameter list in a device control dialog).

  - Selection of devices/parameters for the history plot can now optionally be
    made through a tree widget.

  - Value selections for switcher devices are now sorted by default.

  - Reconnection after lost connection is now less aggressive, to avoid a
    situation with infinite reconnect attempts stalling the daemon.

  - Added an exponential fitting function for history plots.

  - Alias selections in the setup dialog are not touched unless new selections
    for the aliases are enabled by user choice.

  - Added an optional dialog that pops up after a period of inactivity (to
    remind users of changing the experiment if necessary).

  - A watermark image can be displayed in the background of the console panel.

* Tests

  - Tests now use py.test, which has better fixture and reporting support.

Besides these major changes, this release contains a lot of bugfixes and
instrument related changes.


Release 2.11.0
--------------

* GUI

  - The history plotter, as well as the expressions for status monitor
    displays, now understand scale and offset notation like this:
    "dev/value*100+0.7".

  - The history plotter now understands expressions with multiple sub-
    indices, like "dev/value[0][1]".

  - The history plotter now remembers previously opened views and offers
    them for reopening with one click.

  - Scans can now be normalized to the maximum of each curve.

  - Added a sigmoid fitting function.

  - Event masking has been improved in the client protocol, so that live
    detector data is not sent to clients that haven't opened a panel
    that displays it.

  - Fit curves produced by script commands like "gauss" or "sigmoid"
    are now drawn in the scans panel again.

* Commands

  - Added the "sigmoid" command to fit a sigmoid curve from the
    command line.

  - Added a "live" command that starts counting on the detector in the
    background for an unspecified amount of time, which is e.g. useful for
    aligning the instrument or sample.

  - Continuous scans can now be stopped by the regular "stop" command
    between each virtual point.

  - The "numpy" module is now automatically available in the NICOS
    namespace.

* Core

  - Added new utility function "waitForState()" which will wait on a device
    getting into a state passed to the function.

  - The "waitForStatus()" utility function has been renamed to
    "waitForCompletion()" in order to clarify that this function will wait
    for "doIsCompleted()" returning `True` and to avoid confusion with the
    new "waitForState()" function.

  - The code to automatically migrate counter files from the old, pre-2.9
    data handling was removed.

  - Added devices that represent a ROI on an area detector, which can be
    configured by the user, return their total count as a data column,
    and displayed in the GUI.

  - Device parameters are now filled into dataset metainfo from the cache.
    If there are parameters that must be queried from hardware, they
    should either be polled (using "_pollParam") regularly, in a
    "doPoll" method, or specifically before dataset collection, in a
    "doInfo" method.

  - Lowlevel devices are now always created by the session startup.
    Previously, a lowlevel device would only be created when required
    (as attached) by another device.

  - Alias devices can now be non-lowlevel regardless of the lowlevel state
    of their pointee devices.

  - Parameters can now have their own format string used to format param
    values in output.

* Services

  - The error notification email now shows only a manageable excerpt of
    the failed script, with line numbering.

  - The watchdog's precondition handling has been improved.

* Devices

  - The single-crystal diffraction facilities have been significantly
    improved, and a lifting-counter geometry added.

  - HasWindowTimeout now supports "timeout=None" properly.  It also includes
    the window in its time estimation for dry run mode.

  - Added a device that acts as an on/off switch for Tango devices.

  - Readback of targets has been added to EPICS moveables.

  - The virtual image source has been made more realistic.

  - The implementation of the CARESS accessing devices (used at STRESS-SPEC,
    SPODI, and V20 instruments) has been significantly improved.

* Documentation

  - Documentation of GUI widgets has been improved with more pictures, and
    automatic insertion of widget property docstrings.



Release 2.10.0
--------------

* GUI

  - Allow to configure the timefont size as well. This is useful for
    non full-screen display, as they otherwise get quite large.

  - Add cosine as standard fitting function.

  - cmdlets: offer a box for continuous scanning for scan/cscan.

  - Add "finish early and stop" action.

  - Disable dry run buttons during dry run.

  - Add the TAS setup to the Qt designer lib.

  - Display elements of multi-dimensional arrays in status monitor.  This access
    is implemented as listed indices on key values in the configuration.

* Command line client

  - support ~/x paths for /edit, /run etc.

* Commands

  - Reimplementation of 'contscan' with respecting the device limits.

  - In 'scan' command the device values will read after reaching point.

  - 'tomo' command with multiple moveable devices.

* Tools

  - Add 'reformat_setup' tool to format the setup files.

  - 'check_setups' gives errors in case of using 'exclude' instead of
    'excludes'.

* LIMA support

  - Implement image flipping and rotation.

* CARESS support

  - Fix some problems with the simulation.

  - Add 'Driveable' base class.

  - Add missing doStop for the active channels.

  - Add 'histogram' and 'listmode' in QMesyDAQ module.

* EPICS support

  - Add a validator for EPICS PV-names.

  - Make epics test-safe.

* Demo version

  - Improve start/stop of the processes on Windows.

  - Add a virtual STRESS-SPEC instrument.

  - Clean up startup state.

* Documentation

  - Change the HTML style sheet to the 'readthedocs' style.

  - Rearrange and rename the documentation menus.

  - Add some missing documentation for devices/instruments.

  - Restructure the PDF documentation.

  - Add links to the customers in the custom entries.

* Other

  - Add a new parameter tof configure the preferred scattering side of the
    monochromator or analyzer crystal.

  - Improve the test suite.

  - Allow stopping sequencer devices with stop().

  - Fits data sink: add unit to header key values and order the keys
    in header.


Release 2.9.0
-------------

* Version requirements

  - NICOS now requires Python 2.7.

* General behavior

  - Better alias handling: alias preferences are now expressed in setups with
    a new value "alias_config", instead of unconditionally setting aliases
    from startup code.

  - The "instrument" and other special devices are now (attempted to be)
    created when accessed, not only once at setup loading time.

  - Add basic EPICS support.

  - Add basic CARESS support.

  - 'Multi' sample support.

  - Introduction of a new setup type 'configdata'.

  - Detector related mixins.

* GUI

  - Present a choice of aliases in the "load setups" panel.

  - Can now turn off display of watchdog warnings in the status monitor setup.

  - Display a status information if a privileged user is connected to daemon.

  - View only connection (or mode) to daemon.

  - Instrument specific sorted display of loaded setups.

  - Attach/detach windows/tabs/panels and restore after restart.

* Internal changes

  - Completely reworked data api.

* Other

  - Added some demo devices and instruments for presentations.

  - sxtal: single crystal commands and functions.

  - Simple communication protocol support.


Release 2.8.0
-------------

* Commands

  - A "contscan()" can now be stopped without emergency stop while executing.

  - "hklplot()" can now plot multiple "extra points".

* Devices

  - Much more support for Tango devices following the MLZ standard interfaces.

  - Less cryptic Tango error messages.

* GUI

  - The GR plot windows now handling auto scaling much better: scaling can be
    activated separately for X and Y, and the automatically selected plot area
    includes some padding at the edges.

  - The GR plot windows now automatically select a useful X tick distance for
    time series plots.

  - The GR plot window can now copy fit values to the clipboard from a right-
    mouse button context menu.

  - The live view window now supports TIFF files.

  - Added a "shutdown device" entry for the context menu in the device list.

  - The script editor now shows line numbers.

  - Custom commandlets for the script editor are now supported.

* Status monitor

  - The status monitor (GUI and HTML) can now display (and update) images.

  - The status monitor has a more expressive syntax for selecting for which
    setups to display which blocks.

* Other

  - The command-line client can now display ASCII plots using Gnuplot.


Release 2.7.0
-------------

* Commands

  - Errors while executing script commands now don't automatically abort the
    whole script.  Instead, the next command is attempted, but an error
    notification is sent nevertheless.
    You can control this behavior and switch back with the new command
    "SetErrorAbort()".

  - Continuous scans with "contscan()" now have an additional argument to
    specify the integration time, which was always 1 second before.  The X value
    of points is now placed in the middle of the measured intervals.

  - For TAS, added "pos2hkl()".  Without arguments, works like "rp()".  When
    given angle and optionally mono/ana arguments, will calculate the Q/E
    position that these arguments represent.

* Devices

  - There is a new basic mixin "HasTimeout" for devices that should complete
    movement within a specified time.

  - Similarly, for devices that should reach their setpoint within precision for
    a specified time window, there is a new mixin "HasWindowTimeout".

  - The "tolerance" parameter used for some temperature controllers is now
    called "precision", as it expresses the same concept.  "HasPrecision" is now
    always used to provide this parameter.

  - Devices now check for reaching the target position after movement is
    complete.  If the target has not been reached, a warning is emitted for
    normal devices.  For devices with timeout, this also contributes to the
    "movement complete within timeout" condition.

  - A new mixin has been created for communicating devices.  All these devices
    now have a "comtries" and a "comdelay" parameter, which can be used to
    control retries and the sleep time inbetween retries.

  - The "wait()" method is now not a fundamental operation for Moveables
    anymore.  Instead, the method "isCompleted()" has been added, and the
    device-specific concrete method "doIsCompleted()" should be implemented by
    devices.  As with "doWait()" before, writing a "doIsCompleted()" method is
    only necessary if the status information (waiting for non-BUSY status) is
    not sufficient to express completion of movement.

  - Added a new "WARN" device state that should be used to express that the
    device is ok, but there are potential problems the user should be aware of.
    Device values outside the limits defined by the "warnlimits" parameter now
    set the device state to WARN.  Also, moveable devices with values outside
    their userlimits use the WARN state.

* Device classes

  - The Slit class has a new opmode "4blades_opposite", for when the user wants
    to control each blade individually, with mirrored coordinate systems for
    opposing blades.

  - The "GraceSink" for liveplotting with the external Grace program has been
    removed.

  - Some device classes have been renamed to remove redundancies in the module
    and class names.

  - Added a "ReadonlyParamDevice" that returns the value of a device parameter
    on read(), similar to the existing moveable "ParamDevice".

  - Added a common class for FPGA counter cards from FZ Jülich.

* GUI

  - On switching to a new user experiment, the GUI windows now clear information
    still stored/displayed from the old experiment.

  - Errors and warnings that result from an action in a GUI window (for example
    the device control window) should now be shown in a dialog box.

  - The X-axis to use for the plot can now be selected in the scans window.

  - Data can now be normalized to any time or monitor column in the scans
    window.

  - Advanced dataset manipulation (adding, subtracting and dividing datasets)
    now has more sane behavior with respect to normalization and errorbars.

  - Fit results are now shown with errors for the fit parameters.

  - Non-user parameters are shown in the "Devices" panel when expert mode is
    active.

  - The setup dialog now doesn't show plug-and-play setups (for sample
    environment boxes) by default, and there is an option to show them.

  - Added a tool dialog to easily report NICOS bugs to the issue tracker.

* Services

  - The watchdog now can be given preconditions for each warning condition.  To
    emit such a warning, the precondition must be fulfilled for a specified
    time.

  - The init script now checks extensively for existing NICOS processes that
    should not be running, and notifies the user about potential problems.

* Tools

  - A "cache inspector" tool has been added, to inspect the live state of a
    cache database.


Release 2.6.0
-------------

* Commands

  - "appendscan()" can now be used multiple times to append to the original scan
    further and further.

  - The deprecated "DestroyDevice()" has been removed (use "RemoveDevice").

  - The deprecated "Run", "Simulate" and "Notify" commands have been removed
    (use "run", "sim" and "notify").

  - "CreateAllDevices()" now has a flag that allows all lowlevel devices to be
    exported into the NICOS namespace.

  - Common tomography commands for imaging instruments.

* Device classes

  - Devices can now add custom range information to the "device ranges" reported
    after simulation by defining a "_sim_getMinMax" method.

  - MesyDAQ MSTD-16 acquisition hardware is now supported.

  - TACO devices now have more control over mapping the TACO status value to
    NICOS status values without overriding "doStatus()".

  - Added "NamedDigitalInput/Output" and "PartialDigitalInput/Output" to the
    TANGO classes.

  - The "DeviceAlias" has been moved to the "nicos.core" namespace.

  - Devices now support a doPrepare step in scans that is executed before starting
    all devices for a scan point.

* GUI

  - Lowlevel devices are shown in the "Devices" panel when expert mode is
    active.

  - Added a "downtime report" tool to send reports directly to the User Office.

  - History and trend plots can now show subitems of values that are sequences,
    such as "det[0]" for the first channel value of a multi-channel detector.

  - Monitor display widgets can now use a "light background" color scheme.

  - Rename TrendPlot "plotinterval" to "plotwindow" to be consistent between
    history plot and trend plot

  - Daemon: be paranoid about running as root.


* Services

  - When requesting to stop a running script, scripts put into the queue *after*
    the stop command will now be executed after the original script stops.

  - Added a daemon authenticator for LDAP.

  - The init script "nicos-system" is now more careful about really stopping
    services and complaining if they can't be stopped.

  - Watchdog: allow multiple values/devices in conditions.


Release 2.5.0
-------------

* Commands

  - NewExperiment() now warns if the proposal comes from the proposal database
    and has no approval from the radioprotection or safety departments.

  - Added the "setalign()" command for triple-axis mode as an easier alternative
    to manipulating "Sample.psi0" by hand.

  - Added the "activation()" command to query sample activation from the NICOS
    command line using the new FRM II web-based activation calculator.

  - Removed several unused or now obsolete commands: "Remember()", "LogAttach()",
    "Edit()".

  - Added "RemoveDevice()" command as the new preferred way of spelling
    "DestroyDevice()".  The old name will still be available for one version.

  - The "twodscan()" command was changed to run a series of normal 1-dimensional
    scans, so that its result can be plotted and analyzed more easily.

* Device classes

  - A new interface for >= 2-D image data has been implemented in the module
    "nicos.core.image".  It consists of a base class for detectors,
    "ImageProducer", and a base class for image sinks, "ImageSink".  Each
    ImageProducer can have multiple sinks as attached devices.  The image sinks
    are automatically provided with the detector image data and header
    information for use in their data files.

  - Created new HasMapping mixin class for mapped devices, implemented abstract
    MappedReadable and MappedMoveable device skeletons using _readRaw and
    _startRaw methods as counterparts to doRead and doStart, but working with
    mapped (RAW) values.

  - Switcher classes got support for a fallback parameter whose value is
    returned if none of the mapping entries matches.

  - Create a LockedDevice mixin which is used for devices needing a special
    lock/unlock precedure using another device.

  - Added default implementations for "doWait", "doReset", "doStatus" and
    "doStop" that propagate the action to attached devices.

  - TACO temperature controllers can now set the maximum heater power via a
    NICOS parameter.

  - QMesyDAQ detectors are now supported.

  - Astrium selectors are now supported.

  - New VirtualTemperature implementation with more realistic heat flow and PID
    control.

* Other changes

  - Simulation mode: the simulation is now executed in a fresh subprocess, not
    by fork()ing the current NICOS process.  Output from simulation is now saved
    in a log file.  As a consequence, the simulation code cannot use objects in
    the namespace of the running process; they have to be re-created in the
    simulated script.

  - The Experiment device was rewritten to avoid storing copies of the datapath
    in other devices, which might use a stale version under certain
    circumstances.

  - File counters have been made consistent -- there is always just one global
    counter for scan files and image files -- and are now handled by the
    Experiment device.

  - If sending data via email is configured and the attachment gets too big, it
    will be uploaded to a temporary location to be downloaded by the user.

  - The file modes and owners to set on current/old experiment data files can
    now be finely tuned (Experiment.managerights parameter).

* GUI

  - The "experiment setup" panel now allows to finish the experiment with a
    button.

  - The "experiment info" panel now has "..." buttons that directly lead to the
    respective dialogs where the shown item can be changed.

  - The "devices" side panel has been improved: the dialog opened by clicking
    single devices now has more features, such as a graphical way for setting
    limits and referencing devices, and for setting new alias targets.

  - The "setup" panel can now include instrument-specific tabs, like fields to
    enter names of all samples inside a sample changer.

  - The data of a curve displayed in the "Device history" panel can now be saved
    to disk as a plain-text file.

  - When using the "update script" command, the GUI now asks for a reason and
    saves this reason in the experiment log.

* Services

  - The watchdog daemon now can have a unlimited of different condition "types",
    each of which has a separate list of notifiers.

* Documentation

  - TANGO bindings are now documented.

  - Instrument specific setups and some classes are now documented.

* Code modernized for upcoming Python 3 compatibility.

Release 2.4.0
-------------

- An experimental report template can now be automatically filled and placed
  in the experiment directory for user convenience.

- TAS: spurion calculations and warnings are now performed in simulation mode,
  use the "tasdevice.spurioncheck" parameter to control this behavior.

- The "appendscan()" command now appends to the actual end of the scan, not
  the theoretical end (which differs if the scan was interrupted).

- Support for reading values from "Memograph" generated web sites.

- GUI: the elog panel should now allow opening attached files with their default
  viewer (like PDF files).

- GUI: the elog panel now has a print functionality.

- Moveable devices now have a default "doWait()" method that checks for
  the status becoming OK.

- GUI: added a panel to view NICOS log files (if available on the client
  machine).

Release 2.3.0
-------------

- NICOS now requires Python 2.6.

- Added a combined interactive command-input and commandline GUI panel.

- The GUI client now writes a logfile so that unhandled exceptions can be
  better diagnosed.

- Added a MultiSwitcher class to move multiple devices together to pre-
  defined positions.

- Added the "nicos-collector" service that can be used to submit information
  from multiple caches to a "supercache".

- Removed the "SetSMSReceivers" command.

Release 2.2.0
-------------

- Updated documentation describing all NICOS services with configuration
  examples.

- Setups now have more control over which commands are available to the user
  because the standard commands are not automatically loaded anymore.  The
  previous set of standard commands can be loaded via the module
  "nicos.commands.standard".

- Added a "forecast" device that estimates the final number of counts when the
  preset is reached for a counting with a single detector.

- The count loop can now be paused while counting (if the detector supports
  this) by the user or by conditions detected by the watchdog.

- Added "warnlimits" to readable devices, a property that sets a range of
  values outside of which the device value is shown as "out of range" e.g. in
  the status monitor.

- Added a tool to statically check setup files for errors while installing
  NICOS.

- GUI: multiple connection presets are now supported.

- Added pluggable authentication for the NICOS daemon and a backend that
  authenticates against proposal system users.

- Now the user may only release a fixed device if the access level matches or
  exceeds the level of the user who fixed the device.

- GUI: added interactive command input panel.

- GUI: added "device overview/status" panel with a list of all existing
  devices and their values.

- NICOS services and GUI client now run on Windows.

- Added pseudo-devices to read/control the incoming/outgoing energy for
  triple-axis instruments.

- Added readout of the heater power to TACO temperature controllers.

- Added a "requires" parameter to all moveable devices that specifies access
  restrictions for move actions.

- GUI: added ability to create tabbed panel windows and to detach tabs from
  the main window.

- Added a "watchdog" service that reacts to cache events and can send
  notifications or execute actions if an exceptional condition is detected.

- Added a handler for cache events generated by sample environments, so that
  NICOS can automatically suggest loading a particular setup.

- GUI: added a feature to quickly modify data in the liveplot.

- Added the "reference()" command.

- Added a virtual counter implementation for TAS that uses a Monte Carlo
  resolution calculation to simulate intensities for given scattering law
  models.

- Added Eulerian cradle implementation for TAS.

- Added the "info()" command.

- Added a new input mode called "simple parameter mode".  In this mode,
  commands and arguments can be entered without parentheses and
  commas.  Control structures are not supported.  It is toggled with
  the "SetSPM" command.

- Setup files can now also placed in subdirectories of the setup path.
  Entries in parent directories override entries in subdirectories
  when two files have the same name.

- Restructured the "nicos" Python package layout.  Custom libraries
  will have to be adapted.

- Added common FRM II sample environment and reactor setups.  They are
  installed by default for FRM II instruments.

- Added "sweep" scan command.

- The Qt and HTML status monitors can now plot values versus time.

- Added back text-based client for the daemon.

- Changed cache store file format to retain info if the key will expire.
  This fixes cache startup behavior even after unclean shutdowns.

- Added "checkalign" command for TAS instruments.

- Added HTML version of NICOS monitor.

- Added basic mathematical functions and constants in the default namespace.

- Added "resplot" and "hklplot" commands for TAS instruments, which are
  interactive resolution calculation and reciprocal space map helpers.

- Added "alpha" attached-device to triple-axis instrument that is moved
  to the angle between ki and Q whenever the TAS is moved.

- Changed "users" parameter of the experiment device to a simple string,
  and it is now possible to add users directly in "NewExperiment()".

- Added "maxage" parameter to "doRead()" and "doStatus()" methods,
  which can be given to subdevices.

- Added basic TANGO devices.

- Added a "DeviceAlias" object that can be used to refer with one name
  to different actual devices.

- Added graphical help system to the GUI client.  Improved quality of
  docstrings of most commands.

- Added a "mode" parameter to "doInit()" and "doPreinit()" so that
  device implementers remember to check for simulation mode.

- Added an API "Measurable.presetInfo()" that returns the accepted preset
  keys; to check that given presets are actually used by the detector(s).

- Added a new standalone history viewer that plots cache data.

- Improved the message display in the web interface.

- Improved the ELog HTML styling.

- Added a "debug" keyword-only argument to "Simulate()" that prints a
  traceback on exception.

- Added "obsreadings" parameter to generic axis to use instead of the
  hardcoded 100 times when asking observers for the current value.

- Added "history()" method to Grace liveplot.

- History-related commands and methods now accept strings as start and
  end times, e.g. "2012-03-26 12:15".

- Added a "logging_path" setting to nicos.conf.

- Renamed "server" parameter of CacheClient to "cache".

- Added "findpeaks()" analyzing command.

- Changed module structure of the "nicos" Python package to be more logical.

Release 2.1.2
-------------

- Fixed not being able to run another manualscan after stopping a
  manualscan.

- Fixed error in "history()" when calling with actual timestamps.

- Fixed glitches in cache handling of expired values when restarting
  the cache server.

- The cache now re-loads database keys from disk even if not restarted
  on the same day.

- Fixed problem with cache history query not returning all requested
  values.

- Fixed simulation mode not working with no cache configured.

Release 2.1.1
-------------

- Fixed an elog bug that caused elog to quit on Unicode errors.

- Fixed calling "gauss()" and "poly()" with column names.

- Report simulated runtime for code run with "Simulate()".

- Fixed namespaces used in "Run()", so that globals can be accessed from
  functions defined in user scripts.

- Fixed simulating and timing devices with a ramp parameter.

- Made the cache robust against corrupted save files on disk.

- Fixed the "create_nicosconf" script when no TACO environment is found.

- Fixed a bug in simulation mode that would cause exceptions when
  wait()ing for fixed devices.

Release 2.1.0
-------------

- Introduced the "Measurable.duringMeasureHook()" and
  "Measurable.save()/doSave()" methods.

- Added "Experiment.scripts" parameter that stores the code of the
  currently executed script.

- Added easy access control using the "requires()" decorator.  Added
  "AccessError" and "Session.checkAccess()" APIs.

- Added the three-parameter form of "adjust()" that allows to adjust to
  some other than the current position.

- Added automatic retry of Taco calls with the new "tacotries" parameter
  of TacoDevice objects.

- Added the "extended" entry to setup files, for future use.

- The "waitForStatus()" utility function now supports timeout and handling
  error states.

- The "center()" and "checkoffset()" user commands now can take an "ycol"
  keyword that determines which data column is used for fitting.

- Added "calpos()", "pos()" and "rp()" commands for triple-axis
  spectrometers.

- Renamed the "name" setup entry to "description" to match its function.

- Taco motors now can read the absolute limits from the Taco device.

- Removed "setPosition()" from abstract Axis.  Moved "setPosition()" from
  abstract Motor to abstract Coder.

- Changed the "FRMDetector" class to have lists of monitor and counter
  channels as adevs.  Presets are either "t" or "monX" or "ctrX", where
  X is the number of the monitor/counter channel.

- Added suggestion of possible commands when misspelled on the console.

- The TAS commands are not included automatically in setups anymore.

- Added "coordinates" parameter to slits to select the coordinate
  convention for right/left, bottom/top axes.

- Removed first ("converter") argument from parameter type "oneof".

- Added a "FinishExperiment()" user command.

- Added "poll" and "neverpoll" parameters to the Poller object.

- When calling "stop()" without devices, stop all devices in parallel.

- Added "localcontact" parameter for experiment.

- The "pollinterval" parameter of readables can now be None, to disable
  polling.

- The Axis class now has a "jitter" parameter that can account for
  jitter in the movement, e.g. due to airpads.

- Added a "RemoveSetup" command that re-loads everything except for the
  given setups.

- Creating the standard detectors/envlist is now retried every time the
  attribute is accessed from the experiment.

- With option "-c", the NICOS console does not autocreate devices.

- Add "dataroot" parameter for experiment device, which configures actual
  data root path.

- When parameters in configuration are changed, they are now preferred on
  reload to the cached values.

- Temperature controller now respects ramping time for timeout, and allows
  to choose not to raise on timing out.

- Added TAS commands to calculate powder rays and spurion positions.

- Added new "appendscan()" command to quickly append to the last scan.

- Fixed devices now don't raise an exception on moving, but only warn that
  they will not move.

- New command: "Remember()".

- Simplified TACO temperature classes: the temperature control device does
  not have "sample" and "control" channel properties anymore.

Release 2.0.1
-------------

- In "ImageStorage", made sure the data file isn't overwritten unless
  explicitly allowed.

- Fixed the "steps" parameter of IPC coders.

- Fixed nicos.conf not being read.  Prepend PYTHONPATH entries to
  sys.path instead of appending.

- Fixed TAS wavevectors to always move in inverse angstroms.

- Fixed data file counting bug: when two sessions were writing data
  files, they could use the same counter and try to write the same file.

- The Axis now correctly resets the error state on multiple positioning
  tries.

Release 2.0.0
-------------

- Initial release.
