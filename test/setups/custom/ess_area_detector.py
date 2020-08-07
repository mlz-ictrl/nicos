description = 'Setup for the EPICS ADSimDetector.'

pvprefix = '13SIM1:'
detector_channel = 'cam1:'
data_channel = 'image1:'
kafka_channel = 'kafka1:'
kafka_broker = 'ess01.psi.ch:9092'
kafka_topic = 'sim_data_topic'

devices = dict(
    areadetector_base=device(
        'nicos_ess.devices.epics.area_detector.EpicsAreaDetector',
        epicstimeout=3.0,
        description='Area detector instance that can only interact with EPICS',
        unit='',
        statepv=pvprefix + detector_channel + 'DetectorState_RBV',
        startpv=pvprefix + detector_channel + 'Acquire',
        errormsgpv=pvprefix + detector_channel + 'StatusMessage_RBV',
        timers='time_preset'
    ),

    time_preset=device(
        'nicos_ess.devices.epics.detector.EpicsTimerActiveChannel',
        description='Acquisition time preset',
        unit='s',
        readpv=pvprefix + detector_channel + 'AcquireTime_RBV',
        presetpv=pvprefix + detector_channel + 'AcquireTime',
    ),

    time_remaining=device(
        'nicos_ess.devices.epics.detector.EpicsTimerPassiveChannel',
        description='',
        unit='s',
        readpv=pvprefix + detector_channel + 'TimeRemaining_RBV',
    ),

    areadetector_kafka=device(
        'nicos_ess.devices.epics.area_detector.EpicsAreaDetector',
        epicstimeout=3.0,
        description='Area detector instance that can interact with EPICS and read the kafka image stream',
        unit='',
        readpv=pvprefix + detector_channel + 'Acquire_RBV',
        startpv=pvprefix + detector_channel + 'Acquire',
        statepv=pvprefix + detector_channel + 'DetectorState_RBV',
        errormsgpv=pvprefix + detector_channel + 'StatusMessage_RBV',
        timers='time_preset',
        images='kafka_image_channel',
    ),

    kafka_image_channel=device(
        'nicos_ess.devices.kafka.area_detector.ADKafkaImageDetector',
        description='ImageChannel that reads from a kafka stream',
        kafka_plugin='kafka_plugin',
    ),

    kafka_plugin=device(
        'nicos_ess.devices.epics.area_detector.ADKafkaPlugin',
        description='Device that can interact with ADKafkaPlugin',
        kafkapv=pvprefix + kafka_channel,
        brokerpv=pvprefix + kafka_channel + 'KafkaBrokerAddress_RBV',
        topicpv=pvprefix + kafka_channel + 'KafkaTopic_RBV',
        statuspv=pvprefix + kafka_channel + 'ConnectionStatus_RBV',
        msgpv=pvprefix + kafka_channel + 'ConnectionMessage_RBV',
    ),

)
