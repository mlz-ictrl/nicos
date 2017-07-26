NICOS is a network-based control system written for neutron scattering
instruments at the MLZ_.  Its main goals are
flexibility, ease of use and maintenance, and reusability.

NICOS allows remote control of scientific instruments via both interactive
interfaces (GUI, command line) and a scripting system.
The NICOS user scripts are written in Python with some minor restrictions. This
choice allows for very flexible scripts for complex problems and easy
interactive use at the same time.

NICOS features an open interface to allow for different communciation
backends to the underlying hardware. Just to name a few, by default NICOS
supports TACO_, TANGO_, EPICS_, and CARESS_.

NICOS allows runtime changes to the hardware configuration and offers a
plug-and play system for e.g. sample environment systems.

While NICOS was written to control neutron scattering instruments, it is not
limited to these due it's very flexible design.

NICOS offers additional monitoring and log keeping functionality with an
electronic logbook for user activity, a history database for all device
parameters, a background poller, Qt- and html based monitors, and a watchdog
for alerting via email and SMS. Of course, all these features are easily
configurable.

.. _MLZ: http: //www.mlz-garching.de
.. _TACO: http://taco.sf.net
.. _TANGO: http://tango-controls.org
.. _EPICS: http://www.aps.anl.gov/epics/
.. _CARESS: http://www.helmholtz-berlin.de/zentrum/locations/it/software/exsteuer/caress_de.html
