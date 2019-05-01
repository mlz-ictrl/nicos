`AMOR <https://www.psi.ch/sinq/amor/>`_
=======================================

.. automodule:: nicos_ess.devices.epics.detector
.. autoclass:: EpicsPassiveChannel()
.. autoclass:: EpicsActiveChannel()
.. autoclass:: EpicsCounterPassiveChannel()
.. autoclass:: EpicsCounterActiveChannel()
.. autoclass:: EpicsTimerPassiveChannel()
.. autoclass:: EpicsTimerActiveChannel()
.. autoclass:: EpicsDetector()

.. automodule:: nicos_ess.devices.epics.area_detector
.. autoclass:: EpicsAreaDetectorTimerPassiveChannel()
.. autoclass:: EpicsAreaDetector()
.. autoclass:: ADKafkaPlugin()

.. automodule:: nicos_ess.devices.kafka.area_detector
.. autoclass:: ADKafkaImageDetector()
.. autoclass:: HistogramFlatbuffersDeserializer()

.. automodule:: nicos_sinq.devices.epics.scaler_record
.. autoclass:: EpicsScalerRecord()

.. automodule:: nicos_sinq.amor.devices.epics_amor_magnet
.. autoclass:: EpicsAmorMagnet()
.. autoclass:: EpicsAmorMagnetSwitch()

.. automodule:: nicos_sinq.devices.epics.astrium_chopper
.. autoclass:: EpicsChopperSpeed()
.. this class leads to a crash of sphinx:
   AttributeError: 'str' object has no attribute 'ptype'
.. .. autoclass:: EpicsChopperDisc()
.. autoclass:: EpicsAstriumChopper()

.. automodule:: nicos_sinq.amor.devices.chopper
.. autoclass:: AmorChopper()

.. automodule:: nicos_sinq.amor.devices.dimetix
.. autoclass:: EpicsDimetix()

.. automodule:: nicos_sinq.amor.devices.component_handler
.. autoclass:: DistancesHandler()

.. automodule:: nicos_sinq.amor.devices.sps_switch
.. autoclass:: AmorShutter()
.. autoclass:: SpsSwitch()

.. automodule:: nicos_sinq.amor.devices.nexus_updater
.. autoclass:: AmorNexusUpdater()

.. automodule:: nicos_sinq.amor.devices.image_channel
.. autoclass:: AmorSingleDetectorImageChannel()

.. automodule:: nicos_sinq.amor.devices.logical_motor
.. autoclass:: AmorLogicalMotorHandler()
.. autoclass:: AmorLogicalMotor()

.. automodule:: nicos_sinq.amor.devices.hm_config
.. autoclass:: AmorHMConfigurator()
.. autoclass:: AmorTofArray()

.. automodule:: nicos_sinq.amor.devices.datasinks
.. autoclass:: ImageKafkaWithLiveViewDataSink()

.. automodule:: nicos_sinq.amor.devices.slit
.. autoclass:: SlitOpening()

.. automodule:: nicos_sinq.amor.devices.experiment
.. autoclass:: AmorExperiment()

Instrument specific widgets
---------------------------

.. automodule:: nicos_sinq.amor.gui.panels.controlpanel
.. autoclass:: AmorControlPanel()

.. automodule:: nicos_sinq.amor.gui.panels.expinfo
.. autoclass:: AmorExpPanel()

.. automodule:: nicos_sinq.amor.gui.panels.newexp
.. autoclass:: AmorNewExpPanel()

.. automodule:: nicos_sinq.amor.gui.panels.live
.. autoclass:: LiveDataPanel()
