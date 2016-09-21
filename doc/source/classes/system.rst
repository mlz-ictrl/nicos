System devices
==============

These device classes do not represent actual hardware devices, but they use the
same configuration and parameter API as devices and are therefore Device
subclasses.

Experiment
----------

.. module:: nicos.devices.experiment

The experiment device collects all configuration pertaining to the current
experiment -- i.e. proposal information, sample, current configuration of
detectors and sample environment.

The experiment device is selected in setups using :ref:`sysconfig`.

.. autoclass:: Experiment()

.. autoclass:: ImagingExperiment()

.. autoclass:: Sample()


Instrument
----------

.. module:: nicos.devices.instrument

Each setup requires an instrument device, giving basic information and
functionality of the specific instrument.  It is selected in setups using
:ref:`sysconfig`.

.. autoclass:: Instrument()


.. _data_sinks:

Data Sinks
----------

.. todo::

   adapt this

These data sinks provide different ways of processing measured data.  They can
be configured in setups like normal devices and selected in :ref:`sysconfig`.

.. module:: nicos.core.data

.. autoclass:: DataSink()

.. module:: nicos.devices.datasinks

.. autoclass:: ConsoleScanSink()
.. autoclass:: DaemonSink()
.. autoclass:: SerializedSink()

.. autoclass:: LiveViewSink()
.. autoclass:: PNGLiveFileSink()

.. autoclass:: AsciiScanfileSink()

.. autoclass:: ImageSink()

.. autoclass:: SingleRawImageSink()
.. autoclass:: RawImageSink()
.. autoclass:: FITSImageSink()
.. autoclass:: TIFFImageSink()


Data Sink Handlers
^^^^^^^^^^^^^^^^^^

.. currentmodule:: nicos.core.data

.. autoclass:: DataSinkHandler
   :members:


.. _notifiers:

Notifiers
---------

.. module:: nicos.devices.notifiers

These devices provide a way to notify user or instrument responsible.  For
example, in case of unhandled exceptions a notification is always sent if the
script has run for more than a few seconds.

Notifiers can be configured in setups like normal devices and are selected in
:ref:`sysconfig`.  They are also used by the :ref:`watchdog <watchdog>` service.

.. todo::

   add the ``Notifier`` class to the developer section.

.. .. autoclass:: Notifier()

.. autoclass:: Mailer()
.. autoclass:: SMSer()
