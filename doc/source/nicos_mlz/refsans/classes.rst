`REFSANS <http://www.mlz-garching.de/refsans>`_
===============================================


.. module:: nicos_mlz.refsans.devices.nok_support

.. autoclass:: PseudoNOK()
.. autoclass:: NOKMonitoredVoltage()
.. autoclass:: NOKPosition()
.. autoclass:: SingleMotorNOK()
.. autoclass:: DoubleMotorNOK()
.. autoclass:: DoubleMotorAxis()

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
.. autoclass:: DoubleMotorBeckhoff()
.. autoclass:: DoubleMotorBeckhoffNOK()
.. autoclass:: SingleSideRead()
.. autoclass:: SingleMotorOfADoubleMotorNOK()

.. module:: nicos_mlz.refsans.devices.beckhoff.vsd
.. autoclass:: VSDIO()
.. autoclass:: AnalogValue()
.. autoclass:: DigitalValue()

.. module:: nicos_mlz.refsans.devices.gkssjson
.. autoclass:: SdsRatemeter()
.. autoclass:: CPTReadout()
.. autoclass:: CPTReadoutproof()

.. module:: nicos_mlz.refsans.devices.chopper.real
.. autoclass:: ChopperMaster()
.. autoclass:: ChopperDisc()
.. autoclass:: ChopperDisc2()
.. autoclass:: ChopperDiscTranslation()
.. autoclass:: ChopperDiscTranslationEncoder()

.. module nicos_mlz.refsans.devices.chopper.base
.. autoclass SeqSlowParam(SeqParam):
.. autoclass SeqFuzzyParam(SeqParam):
.. module nicos_mlz.refsans.devices.chopper.virtual
.. autoclass ChopperDisc1(ChopperDisc):

.. module:: nicos_mlz.refsans.devices.skew_motor
.. autoclass:: SkewRead()
.. autoclass:: SkewMotor()

.. module:: nicos_mlz.refsans.devices.analogencoder
.. autoclass:: AnalogEncoder()
.. autoclass:: AnalogMove()

.. module:: nicos_mlz.refsans.devices.sample
.. autoclass:: Sample()

.. module:: nicos_mlz.refsans.devices.accuracy
.. autoclass:: Accuracy()

.. module:: nicos_mlz.refsans.devices.det_yoke_enc
.. autoclass:: BasePos()

.. module:: nicos_mlz.refsans.devices.avg
.. autoclass::  BaseAvg()

.. module:: nicos_mlz.refsans.devices.beamstop
.. autoclass:: BeamStopDevice()
.. autoclass:: BeamStopCenter()

.. module:: nicos_mlz.refsans.devices.controls
.. autoclass:: SeqWaitConditional()
.. autoclass:: TemperatureControlled()

.. module:: nicos_mlz.refsans.devices.converters
.. autoclass:: Ttr()
.. autoclass Coder()
.. autoclass Moveable()

.. module:: nicos_mlz.refsans.devices.devicealias
.. autoclass:: HighlevelDeviceAlias()

.. module:: nicos_mlz.refsans.devices.dimetix
.. autoclass:: DimetixLaser()

.. module:: nicos_mlz.refsans.devices.expertvibro8
.. autoclass:: Base()
.. autoclass:: AnalogValue()

.. module:: nicos_mlz.refsans.devices.focuspoint
.. autoclass:: FocusPoint()

.. module:: nicos_mlz.refsans.devices.nima
.. autoclass:: ReadName()
.. autoclass:: MoveName()
.. autoclass:: Area()
.. autoclass:: Press()

.. module:: nicos_mlz.refsans.devices.pivot
.. autoclass:: PivotPoint()

.. module:: nicos_mlz.refsans.devices.psutil
.. autoclass:: CPUPercentage()
.. autoclass:: ProcessIdentifier()

.. module:: nicos_mlz.refsans.devices.resolution
.. autoclass:: Resolution()
.. autoclass:: RealFlightPath()

.. module:: nicos_mlz.refsans.devices.safetysystem
.. autoclass:: Shs()
.. autoclass:: Group()

.. module:: nicos_mlz.refsans.devices.shutter
.. autoclass:: Shutter(Switcher)

.. module:: nicos_mlz.refsans.devices.syringepump
.. autoclass:: PumpAnalogOutput()

.. module:: nicos_mlz.refsans.devices.triangle
.. autoclass:: TriangleBase()
.. autoclass:: TriangleMaster()
.. autoclass:: TriangleAngle()

.. module:: nicos_mlz.refsans.devices.tristate
.. autoclass:: TriState()

.. module:: nicos_mlz.refsans.devices.tube
.. autoclass:: TubeAngle()

Data Sinks
----------

.. module:: nicos_mlz.refsans.datasinks
.. autoclass:: ConfigObjDatafileSink()

Instrument specific widgets
---------------------------

.. module:: nicos_mlz.refsans.gui.monitorwidgets
.. autoclass:: VRefsans()
.. autoclass:: BeamPosition()
.. autoclass:: TimeDistance()

Mixin classes (only for developers)
-----------------------------------

.. module:: nicos_mlz.refsans.devices.mixins
.. autoclass:: PseudoNOK()
.. autoclass:: PolynomFit()
