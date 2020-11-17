NICOS is a network-based control system originally written for neutron
scattering instruments at the MLZ_.  Its main goals are flexibility, ease of
use and maintenance, and reusability.

NICOS allows remote control of scientific instruments via both interactive
interfaces (GUI, command line) and a scripting system.
The NICOS user scripts are written in Python with some minor restrictions.
This choice allows for very flexible scripts for complex problems and easy
interactive use at the same time.

NICOS features an open interface to allow for different communciation backends
to the underlying hardware. Just to name a few, by default NICOS supports
TACO_, TANGO_, EPICS_, CARESS_, and SECoP_.

NICOS allows runtime changes to the hardware configuration and offers a
plug-and play system for e.g. sample environment systems.

While NICOS' initial use case was to control neutron scattering instruments,
it is not limited to these due its very flexible design.

NICOS offers additional monitoring and log keeping functionality with an
electronic logbook for user activity, a history database for all device
parameters, a background poller, Qt and HTML based monitors, and a watchdog
for alerting via email and instant messaging services (such as Slack).
Of course, all these features are easily configurable.

.. _MLZ: https: //www.mlz-garching.de
.. _TACO: https://taco.sf.net
.. _TANGO: https://tango-controls.org
.. _EPICS: https://www.aps.anl.gov/epics/
.. _CARESS: https://www.helmholtz-berlin.de/zentrum/locations/it/software/exsteuer/caress_de.html
.. _SECoP: https://github.com/SampleEnvironment/SECoP
