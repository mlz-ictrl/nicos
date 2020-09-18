`REFSANS <http://www.mlz-garching.de/refsans>`_
===============================================


.. automodule:: nicos_mlz.refsans.devices.nok_support

.. autoclass:: PseudoNOK()
.. autoclass:: NOKMonitoredVoltage()
.. autoclass:: NOKPosition()
.. autoclass:: NOKMotorIPC()
.. autoclass:: SingleMotorNOK()
.. autoclass:: DoubleMotorNOK()
.. autoclass:: DoubleMotorNOKIPC()
.. autoclass:: DoubleMotorNOKBeckhoff()

.. automodule:: nicos_mlz.refsans.devices.slits

.. autoclass:: SingleSlit()
.. autoclass:: DoubleSlit()
.. autoclass:: DoubleSlitSequence()
.. autoclass:: SingleSlitAxis()

.. automodule:: nicos_mlz.refsans.devices.optic
.. autoclass:: Optic()

.. automodule:: nicos_mlz.refsans.devices.beckhoff.nok
.. autoclass:: BeckhoffMotorCab1()
.. autoclass:: BeckhoffMotorCab1M0x()
.. autoclass:: BeckhoffMotorCab1M13()
.. autoclass:: BeckhoffMotorDetector()
.. autoclass:: BeckhoffCoderDetector()
.. autoclass:: BeckhoffMotorHSlit()
.. autoclass:: DoubleMotorBeckhoff()
.. autoclass:: DoubleMotorBeckhoffNOK()
.. autoclass:: SingleSideRead()
.. autoclass:: SingleMotorOfADoubleNOK()

.. automodule:: nicos_mlz.refsans.devices.beckhoff.pumpstation
.. autoclass:: PumpstandIO()
.. autoclass:: PumpstandPressure()
.. autoclass:: PumpstandPump()

.. automodule:: nicos_mlz.refsans.devices.beckhoff.vsd
.. autoclass:: VSDIO()
.. autoclass:: AnalogValue()
.. autoclass:: DigitalValue()

.. automodule:: nicos_mlz.refsans.devices.detector
.. autoclass:: ComtecCounter()
.. autoclass:: ComtecTimer()
.. autoclass:: ComtecFilename()

.. automodule:: nicos_mlz.refsans.devices.gkssjson
.. autoclass:: SdsRatemeter()
.. autoclass:: CPTReadout()

.. automodule:: nicos_mlz.refsans.devices.chopper.real
.. autoclass:: ChopperMaster()
.. autoclass:: ChopperDisc()
.. autoclass:: ChopperDisc2()
.. autoclass:: ChopperDiscTranslation()

.. automodule:: nicos_mlz.refsans.devices.skew_motor
.. autoclass:: SkewRead()
.. autoclass:: SkewMotor()

.. automodule:: nicos_mlz.refsans.devices.analogencoder
.. autoclass:: AnalogEncoder()
.. autoclass:: AnalogMove()

.. automodule:: nicos_mlz.refsans.devices.sample
.. autoclass:: Sample()

.. automodule:: nicos_mlz.refsans.devices.det_yoke_enc
.. autoclass:: BasePos()

Data Sinks
----------

.. automodule:: nicos_mlz.refsans.devices.datasinks
.. autoclass:: ConfigObjDatafileSink()

.. currentmodule:: nicos_mlz.refsans.devices.detector
.. autoclass:: ComtecHeaderSink()

Instrument specific widgets
---------------------------

.. automodule:: nicos_mlz.refsans.gui.monitorwidgets
.. autoclass:: VRefsans()
.. autoclass:: BeamPosition()
.. autoclass:: TimeDistance()
