System devices
==============

These device classes do not represent actual hardware devices, but they use the
same configuration and parameter API as devices and are therefore Device
subclasses.

Experiment
----------

.. module:: nicos.experiment

The experiment device collects all configuration pertaining to the current
experiment -- i.e. proposal information, sample, current configuration of
detectors and sample environment.

The experiment device is selected in setups using :ref:`sysconfig`.

.. autoclass:: Experiment()

.. autoclass:: Sample()


Instrument
----------

.. module:: nicos.instrument

Each setup requires an instrument device, giving basic information and
functionality of the specific instrument.  It is selected in setups using
:ref:`sysconfig`.

.. autoclass:: Instrument()


Data Sinks
----------

These data sinks provide different ways of processing scan data.  They can be
configured in setups like normal devices and selected in :ref:`sysconfig`.

.. module:: nicos.core.data

.. autoclass:: DataSink()

.. module:: nicos.data

.. autoclass:: ConsoleSink()
.. autoclass:: AsciiDatafileSink()
.. autoclass:: GraceSink()
.. autoclass:: GnuplotSink()
.. autoclass:: DaemonSink()


Notifiers
---------

.. module:: nicos.notify

These devices provide a way to notify user or instrument responsible.  For
example, in case of unhandled exceptions a notification is always sent if the
script has run for more than a few seconds.

Notifiers can be configured in setups like normal devices and are selected in
:ref:`sysconfig`.

.. autoclass:: Notifier()

.. autoclass:: Mailer()
.. autoclass:: SMSer()
.. autoclass:: Jabberer()
