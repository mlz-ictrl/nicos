User Commands
=============

Getting help
------------

.. autofunction:: nicos.commands.basic.help
.. autofunction:: nicos.commands.basic.listcommands
.. autofunction:: nicos.commands.device.listdevices
.. autofunction:: nicos.commands.device.listparams
.. autofunction:: nicos.commands.device.listmethods
.. autofunction:: nicos.commands.device.listallparams
.. autofunction:: nicos.commands.device.version

Output commands
---------------

These commands can be used from user scripts to print information to the output
and the logfile.

.. module:: nicos.commands.output

.. autofunction:: printinfo
.. autofunction:: printdebug
.. autofunction:: printwarning
.. autofunction:: printerror
.. autofunction:: printexception

Setup-related commands
----------------------

.. module:: nicos.commands.basic

.. autofunction:: NewSetup
.. autofunction:: AddSetup
.. autofunction:: ListSetups
.. autofunction:: CreateDevice
.. autofunction:: CreateAllDevices
.. autofunction:: DestroyDevice
.. autofunction:: SetMode

Experiment-related commands
---------------------------

.. autofunction:: NewExperiment
.. autofunction:: AddUser
.. autofunction:: NewSample
.. autofunction:: Remark
.. autofunction:: LogEntry
.. autofunction:: LogAttach

Script-related commands
-----------------------

Do not use these commands from the GUI client, rather use its editor which
provides Run and Simulate commands.

.. autofunction:: Edit
.. autofunction:: Run
.. autofunction:: Simulate

Notification commands
---------------------

.. autofunction:: Notify
.. autofunction:: SetMailReceivers
.. autofunction:: SetSMSReceivers

Miscellaneous commands
----------------------

.. autofunction:: sleep
.. autofunction:: Keep
.. autofunction:: ClearCache
.. autofunction:: UserInfo
.. autofunction:: SaveSimulationSetup

Device commands
---------------

.. module:: nicos.commands.device

.. autofunction:: read
.. autofunction:: status
.. autofunction:: limits

.. autofunction:: move
.. autofunction:: wait
.. autofunction:: maw
.. autofunction:: stop
.. autofunction:: reset

.. autofunction:: fix
.. autofunction:: release

.. autofunction:: adjust

Measuring commands
------------------

.. module:: nicos.commands.measure

.. autofunction:: count
.. autofunction:: preset
.. autofunction:: SetDetectors
.. autofunction:: SetEnvironment

Scanning commands
-----------------

.. module:: nicos.commands.scan

.. autofunction:: scan
.. autofunction:: cscan
.. autofunction:: timescan
.. autofunction:: contscan
.. autofunction:: manualscan

Triple-axis commands
--------------------

.. module:: nicos.commands.tas

.. autofunction:: qscan
.. autofunction:: qcscan
.. autofunction:: Q
