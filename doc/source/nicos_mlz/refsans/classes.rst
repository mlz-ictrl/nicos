`REFSANS <http://www.mlz-garching.de/refsans>`_
===============================================


.. module:: nicos_mlz.refsans.devices.nok_support

.. autoclass:: PseudoNOK()
.. autoclass:: NOKMonitoredVoltage()
.. autoclass:: NOKPosition()
.. autoclass:: SingleMotorNOK()
.. autoclass:: DoubleMotorNOK()
.. autoclass:: DoubleMotorNOKIPC()

.. module:: nicos_mlz.refsans.devices.ipc
.. autoclass:: NOKMotorIPC()

.. module:: nicos_mlz.refsans.devices.slits

.. autoclass:: SingleSlit()
.. autoclass:: DoubleSlit()
.. autoclass:: DoubleSlitSequence()
.. autoclass:: SingleSlitAxis()

.. module:: nicos_mlz.refsans.devices.optic
.. autoclass:: Optic()

.. module:: nicos_mlz.refsans.devices.beckhoff.nok
.. autoclass:: BeckhoffMotorCab1()
.. autoclass:: BeckhoffMotorCab1M0x()
.. autoclass:: BeckhoffMotorCab1M13()
.. autoclass:: BeckhoffMotorDetector()
.. autoclass:: BeckhoffCoderDetector()
.. autoclass:: DoubleMotorBeckhoff()
.. autoclass:: DoubleMotorBeckhoffNOK()
.. autoclass:: SingleSideRead()

.. module:: nicos_mlz.refsans.devices.beckhoff.vsd
.. autoclass:: VSDIO()
.. autoclass:: AnalogValue()
.. autoclass:: DigitalValue()

.. module:: nicos_mlz.refsans.devices.detector
.. autoclass:: ComtecCounter()
.. autoclass:: ComtecTimer()
.. autoclass:: ComtecFilename()

.. module:: nicos_mlz.refsans.devices.gkssjson
.. autoclass:: SdsRatemeter()
.. autoclass:: CPTReadout()

.. module:: nicos_mlz.refsans.devices.chopper.real
.. autoclass:: ChopperMaster()
.. autoclass:: ChopperDisc()
.. autoclass:: ChopperDisc2()
.. autoclass:: ChopperDiscTranslation()

.. module:: nicos_mlz.refsans.devices.skew_motor
.. autoclass:: SkewRead()
.. autoclass:: SkewMotor()

.. module:: nicos_mlz.refsans.devices.analogencoder
.. autoclass:: AnalogEncoder()
.. autoclass:: AnalogMove()

.. module:: nicos_mlz.refsans.devices.sample
.. autoclass:: Sample()

.. module:: nicos_mlz.refsans.devices.analog
.. autoclass:: AnalogPoly()
.. autoclass:: AnalogCalc()
.. autoclass:: Accuracy()

.. module:: nicos_mlz.refsans.devices.det_yoke_enc
.. autoclass:: BasePos()

Data Sinks
----------

.. module:: nicos_mlz.refsans.devices.datasinks
.. autoclass:: ConfigObjDatafileSink()

.. currentmodule:: nicos_mlz.refsans.devices.detector
.. autoclass:: ComtecHeaderSink()

Instrument specific widgets
---------------------------

.. module:: nicos_mlz.refsans.gui.monitorwidgets
.. autoclass:: VRefsans()
.. autoclass:: BeamPosition()
.. autoclass:: TimeDistance()
