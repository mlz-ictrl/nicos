User Commands
=============

- `Getting help`_
- `Device commands`_
- `Scanning commands`_
- `Output commands`_
- `Setup-related commands`_
- `Experiment-related commands`_
- `Sample-related commands`_
- `Script-related commands`_
- `Simulation mode commands`_
- `Notification commands`_
- `Miscellaneous commands`_
- `On-line analysis commands`_
- `Triple-axis commands`_
- `Imaging commands`_
- `Sample utility functions`_
- `Simple parameter mode`_

Getting help
------------

.. module:: nicos.commands.basic

.. autofunction:: help
.. autofunction:: ListCommands

.. module:: nicos.commands.device
.. autofunction:: ListDevices
.. autofunction:: ListParams
.. autofunction:: ListMethods
.. autofunction:: version

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

.. currentmodule:: nicos.commands.basic

.. autofunction:: NewSetup
.. autofunction:: AddSetup
.. autofunction:: RemoveSetup
.. autofunction:: ListSetups
.. autofunction:: CreateDevice
.. autofunction:: CreateAllDevices
.. autofunction:: RemoveDevice
.. autofunction:: SetMode

Experiment-related commands
---------------------------

.. autofunction:: NewExperiment

.. autofunction:: Remark
.. autofunction:: LogEntry
.. autofunction:: FinishExperiment

Script-related commands
-----------------------

.. autofunction:: run
.. autofunction:: pause
.. autofunction:: abort

Simulation mode commands
------------------------

.. autofunction:: sim
.. autofunction:: sync

Notification commands
---------------------

.. autofunction:: notify
.. autofunction:: SetMailReceivers
.. autofunction:: SetDataReceivers

Miscellaneous commands
----------------------

.. autofunction:: sleep
.. .. autofunction:: Keep
.. autofunction:: ClearCache
.. .. autofunction:: UserInfo
.. autofunction:: SetErrorAbort
.. autofunction:: SetSimpleMode

   See spm_.

Device commands
---------------

.. currentmodule:: nicos.commands.device

.. autofunction:: read

.. autofunction:: move
.. autofunction:: maw
.. autofunction:: rmove
.. autofunction:: rmaw
.. autofunction:: stop

.. autofunction:: status

.. autofunction:: reset
.. autofunction:: wait
.. autofunction:: waitfor
.. autofunction:: info

.. autofunction:: limits
.. autofunction:: resetlimits

.. autofunction:: fix
.. autofunction:: release

.. autofunction:: adjust
.. autofunction:: reference

.. autofunction:: disable
.. autofunction:: enable

.. autofunction:: history

.. autofunction:: getall
.. autofunction:: setall

Measuring commands
------------------

.. module:: nicos.commands.measure

.. autofunction:: count
.. autofunction:: preset

.. autofunction:: SetDetectors
.. autofunction:: AddDetector
.. autofunction:: ListDetectors

.. autofunction:: SetEnvironment
.. autofunction:: AddEnvironment
.. autofunction:: ListEnvironment
.. autofunction:: ListDatasinks
.. autofunction:: avg
.. autofunction:: minmax

Scanning commands
-----------------

.. module:: nicos.commands.scan

.. autofunction:: scan
.. autofunction:: cscan
.. autofunction:: timescan
.. autofunction:: sweep
.. autofunction:: contscan
.. autofunction:: appendscan
.. autofunction:: manualscan
.. autofunction:: gridscan

On-line analysis commands
-------------------------

.. module:: nicos.commands.analyze

.. autofunction:: center_of_mass
.. autofunction:: root_mean_square
.. autofunction:: fwhm
.. autofunction:: poly
.. autofunction:: gauss
.. autofunction:: findpeaks
.. autofunction:: center
.. autofunction:: checkoffset

Triple-axis commands
--------------------

To use these commands, add ``'nicos.commands.tas'`` to the ``modules`` list of
one of your loaded setups.

.. module:: nicos.commands.tas

.. autofunction:: Q
.. autofunction:: qscan
.. autofunction:: qcscan
.. autofunction:: calpos
.. autofunction:: pos
.. autofunction:: pos2hkl
.. autofunction:: setalign
.. autofunction:: checkalign

.. autofunction:: alu
.. autofunction:: copper
.. autofunction:: ho_spurions
.. autofunction:: acc_bragg

Imaging commands
----------------

To use these commands, add ``'nicos.commands.imaging'`` to the ``modules`` list of
one of your loaded setups.  Additionally, your experiment device has to be an
:class:`~nicos.devices.experiment.ImagingExperiment`.

.. module:: nicos.commands.imaging

.. autofunction:: tomo
.. autofunction:: grtomo

.. module:: nicos_mlz.frm2.commands.imaging

.. autofunction:: openbeamimage
.. autofunction:: darkimage

Sample-related commands
-----------------------

.. module:: nicos.commands.sample

.. autofunction:: NewSample
.. autofunction:: SetSample
.. autofunction:: ListSamples
.. autofunction:: SelectSample
.. autofunction:: ClearSamples

Sample utility functions
------------------------

.. autofunction:: activation


Simple parameter mode
---------------------

.. _spm:

.. automodule:: nicos.core.spm
   :no-members:
