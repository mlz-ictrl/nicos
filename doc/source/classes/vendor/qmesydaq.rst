QMesyDAQ classes
================

.. module:: nicos.devices.vendor.qmesydaq

These classes are for integration of detectors with MesyTec hardware and
controlled by `QMesyDAQ <http://forge.frm2.tum.de/projects/qmesydaq>`_.
Communication works via the TACO interface of QMesyDAQ.

All classes are channels and must be combined to a detector device with the
:class:`~nicos.devices.generic.detector.Detector`.

.. autoclass:: Timer()

.. autoclass:: Counter()

.. autoclass:: MultiCounter()

.. autoclass:: Image()

.. autoclass:: Filenames()
