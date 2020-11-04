`AMOR <https://www.psi.ch/sinq/amor/>`_
=======================================

.. module:: nicos_ess.devices.epics.detector
.. autoclass:: EpicsPassiveChannel()
.. autoclass:: EpicsActiveChannel()
.. autoclass:: EpicsCounterPassiveChannel()
.. autoclass:: EpicsCounterActiveChannel()
.. autoclass:: EpicsTimerPassiveChannel()
.. autoclass:: EpicsTimerActiveChannel()
.. autoclass:: EpicsDetector()

.. module:: nicos_ess.devices.epics.area_detector
.. autoclass:: EpicsAreaDetectorTimerPassiveChannel()
.. autoclass:: EpicsAreaDetector()
.. autoclass:: ADKafkaPlugin()

.. module:: nicos_ess.devices.kafka.area_detector
.. autoclass:: ADKafkaImageDetector()
.. autoclass:: HistogramFlatbuffersDeserializer()

.. module:: nicos_sinq.devices.epics.scaler_record
.. autoclass:: EpicsScalerRecord()

.. module:: nicos_sinq.amor.devices.epics_amor_magnet
.. autoclass:: EpicsAmorMagnet()
.. autoclass:: EpicsAmorMagnetSwitch()

.. module:: nicos_sinq.devices.epics.astrium_chopper
.. autoclass:: EpicsChopperSpeed()
.. this class leads to a crash of sphinx:
   AttributeError: 'str' object has no attribute 'ptype'
.. .. autoclass:: EpicsChopperDisc()
.. autoclass:: EpicsAstriumChopper()

.. module:: nicos_sinq.amor.devices.chopper
.. autoclass:: AmorChopper()

.. module:: nicos_sinq.amor.devices.dimetix
.. autoclass:: EpicsDimetix()

.. module:: nicos_sinq.amor.devices.component_handler
.. autoclass:: DistancesHandler()

.. module:: nicos_sinq.amor.devices.sps_switch
.. autoclass:: AmorShutter()
.. autoclass:: SpsSwitch()

.. module:: nicos_sinq.amor.devices.nexus_updater
.. autoclass:: AmorNexusUpdater()

.. module:: nicos_sinq.amor.devices.image_channel
.. autoclass:: AmorSingleDetectorImageChannel()

.. module:: nicos_sinq.amor.devices.logical_motor
.. autoclass:: AmorLogicalMotorHandler()
.. autoclass:: AmorLogicalMotor()

.. module:: nicos_sinq.amor.devices.hm_config
.. autoclass:: AmorHMConfigurator()
.. autoclass:: AmorTofArray()

.. module:: nicos_sinq.amor.devices.datasinks
.. autoclass:: ImageKafkaWithLiveViewDataSink()

.. module:: nicos_sinq.amor.devices.slit
.. autoclass:: SlitOpening()

.. module:: nicos_sinq.amor.devices.experiment
.. autoclass:: AmorExperiment()

Instrument specific widgets
---------------------------

.. module:: nicos_sinq.amor.gui.panels.controlpanel
.. autoclass:: AmorControlPanel()

.. module:: nicos_sinq.amor.gui.panels.expinfo
.. autoclass:: AmorExpPanel()

.. module:: nicos_sinq.amor.gui.panels.newexp
.. autoclass:: AmorNewExpPanel()

.. module:: nicos_sinq.amor.gui.panels.live
.. autoclass:: LiveDataPanel()
