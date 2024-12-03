SINQ classes
============

.. module:: nicos_sinq.devices.beamoracle
.. autoclass:: BeamOracle

.. module:: nicos_sinq.devices.camini
.. autoclass:: WaitPV
.. autoclass:: WaitThreshold
.. autoclass:: WaitNotPV
.. autoclass:: PutPV
.. autoclass:: Message
.. autoclass:: CaminiDetector
.. autoclass:: CaminiTrigger

.. module:: nicos_sinq.devices.ccdcontrol
.. autoclass:: NIAGControl

.. module:: nicos_sinq.devices.channel
.. autoclass:: SelectSliceImageChannel
.. autoclass:: ReadableToChannel

.. module:: nicos_sinq.devices.datasinks
.. autoclass:: SinqNexusFileSinkHandler
.. autoclass:: SinqNexusFileSink
.. autoclass:: QuieckHandler
.. autoclass:: QuieckSink
.. autoclass:: SwitchableNexusSink
.. autoclass:: ImageForwarderSinkHandler
.. autoclass:: ImageForwarderSink

.. module:: nicos_sinq.devices.detector
.. autoclass:: SinqDetector
.. autoclass:: ControlDetector

.. module:: nicos_sinq.devices.doublemono
.. autoclass:: DoubleMonochromator

.. module:: nicos_sinq.devices.epics.SINQ_area_detector
.. autoclass:: AndorAreaDetector

.. module:: nicos_sinq.devices.epics.__init__
.. autoclass:: EpicsDigitalMoveable
.. autoclass:: EpicsReadable

.. module:: nicos_sinq.devices.epics.area_detector
.. autoclass:: EpicsAreaDetectorTimerPassiveChannel
.. autoclass:: EpicsAreaDetector
.. autoclass:: ADKafkaPlugin
.. autoclass:: ADImageChannel

.. module:: nicos_sinq.devices.epics.astrium_chopper
.. autoclass:: EpicsChopperSpeed
.. autoclass:: EpicsChopperDisc
.. autoclass:: EpicsAstriumChopper

.. module:: nicos_sinq.devices.epics.generic
.. autoclass:: WindowMoveable
.. autoclass:: EpicsArrayReadable

.. module:: nicos_sinq.devices.epics.motor_deprecated
.. autoclass:: EpicsMotor

.. module:: nicos_sinq.devices.epics.motor
.. autoclass:: SinqMotor

.. module:: nicos_sinq.devices.epics.proton_counter
.. autoclass:: SINQProtonCurrent
.. autoclass:: SINQProtonCharge

.. module:: nicos_sinq.devices.epics.scaler_record
.. autoclass:: EpicsScalerRecord

.. module:: nicos_sinq.devices.experiment
.. autoclass:: SinqDataManager
.. autoclass:: SinqExperiment
.. autoclass:: TomoSinqExperiment

.. module:: nicos_sinq.devices.illasciisink
.. autoclass:: ILLAsciiHandler
.. autoclass:: ILLAsciiSink
.. autoclass:: ILLAsciiScanfileReader

.. module:: nicos_sinq.devices.interpolatedmotor
.. autoclass:: InterpolatedMotor

.. module:: nicos_sinq.devices.kafka.area_detector
.. autoclass:: ADKafkaImageDetector
.. autoclass:: HistogramFlatbuffersDeserializer

.. module:: nicos_sinq.devices.lin2ang
.. autoclass:: Lin2Ang

.. module:: nicos_sinq.devices.logical_motor
.. autoclass:: InterfaceLogicalMotorHandler
.. autoclass:: LogicalMotor

.. module:: nicos_sinq.devices.mono
.. autoclass:: SinqMonochromator
.. autoclass:: TasAnalyser

.. module:: nicos_sinq.devices.niag_shutter
.. autoclass:: NiagShutter
.. autoclass:: NiagExpShutter

.. module:: nicos_sinq.devices.procdevice
.. autoclass:: ProcDevice

.. module:: nicos_sinq.devices.s5_switch
.. autoclass:: S5Switch
.. autoclass:: AmorShutter
.. autoclass:: S5Bit
.. autoclass:: SpsReadable

.. module:: nicos_sinq.devices.s7_switch
.. autoclass:: S7Switch
.. autoclass:: S7Shutter

.. module:: nicos_sinq.devices.sinqasciisink
.. autoclass:: SINQAsciiSinkHandler
.. autoclass:: SINQAsciiSink

.. module:: nicos_sinq.devices.sinqhm.channel
.. autoclass:: HistogramImageChannel
.. autoclass:: ReshapeHistogramImageChannel
.. autoclass:: HistogramMemoryChannel

.. module:: nicos_sinq.devices.sinqhm.configurator
.. autoclass:: HistogramConfElement
.. autoclass:: HistogramConfArray
.. autoclass:: HistogramConfTofArray
.. autoclass:: HistogramConfAxis
.. autoclass:: HistogramConfBank
.. autoclass:: ConfiguratorBase

.. module:: nicos_sinq.devices.sinqhm.connector
.. autoclass:: HttpConnector

.. module:: nicos_sinq.devices.storedpositions
.. autoclass:: StoredPositions

.. module:: nicos_sinq.devices.tassinq
.. autoclass:: SinqTAS

.. module:: nicos_sinq.devices.velocity_selector
.. autoclass:: VSForbiddenMoveable
.. autoclass:: VSTiltMotor
.. autoclass:: VSLambda

.. module:: nicos_sinq.devices.wall_time
.. autoclass:: WallTime

.. module:: nicos_sinq.devices.noptic
.. autoclass:: NODirector
