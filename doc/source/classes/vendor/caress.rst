CARESS accessing device classes
===============================

CARESS is the instrument control software for the neutron scattering
instruments at the `Helmholtz Zentrum Berlin (HZB) <https://www.helmholtz-berlin.de/>`_ .

It is split into 2 parts, the graphical user interface and the hardware
devices drivers.  Since the hardware device drivers may run without the GUI
the existing hardware (and the drivers) could be used with NICOS too (at
the moment used at SPODI and STRESS-SPEC instruments at the
`MLZ <https://www.mlz-garching.de>`_, and at V20 at the HZB).

.. _HZB: <https://www.helmholtz-berlin.de/>

.. module:: nicos.devices.vendor.caress.base

.. autoclass:: Driveable

.. module:: nicos.devices.vendor.caress.core

.. autoclass:: CARESSDevice

.. module:: nicos.devices.vendor.caress.motor

.. autoclass:: Motor
.. autoclass:: EKFMotor
.. autoclass:: MuxMotor

.. module:: nicos.devices.vendor.caress.mux

.. autoclass:: MUX
