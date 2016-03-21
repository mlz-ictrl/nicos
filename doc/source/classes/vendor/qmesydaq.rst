QMesyDAQ classes
================

These classes are for integration of detectors with MesyTec hardware and
controlled by `QMesyDAQ <http://forge.frm2.tum.de/projects/qmesydaq>`_.
Communication works via the TACO interface of QMesyDAQ.

All classes are channels and must be combined to a detector device with the
:class:`~nicos.devices.generic.detector.Detector`.

There are two versions of the classes: one version where communication with
QMesyDAQ is done via TACO, the other where communication is done via CARESS.

.. module:: nicos.devices.vendor.qmesydaq.taco

.. autoclass:: Timer()
.. autoclass:: Counter()
.. autoclass:: MultiCounter()
.. autoclass:: Image()

.. module:: nicos.devices.vendor.qmesydaq.caress

.. autoclass:: Timer()
.. autoclass:: Counter()
.. autoclass:: Image()
