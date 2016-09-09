NICOS is a network-based control system written for neutron scattering
instruments at the `MLZ <http://www.mlz-garching.de/>`_.  Its main goals are
flexibility, ease of use and maintenance, and reusability.

NICOS is an instrument control system which allows a 24/7 remote control of
scientific instruments.  It was developed at the FRM-II (as a part of the MLZ)
to control the neutron experiments. It is not limited in use for these
instruments since it was designed to be very flexible.

One major goal during the development of NICOS was, that it must be open for
extensions.

The flexibility in use is mainly given by the syntax for the so-called user
scripts.  The user may program their experiment(s) for long term running as well
as for interactive use.

The language for the user scripts is Python with some minor restrictions.  For
example, it is not allowed to re-assign any names pointing to instrument
specific devices and commands (functions).
