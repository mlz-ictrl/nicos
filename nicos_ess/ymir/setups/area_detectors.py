description = 'The area detector for YMIR'

devices = dict(
    flir_kafka_plugin=device(
        'nicos_ess.devices.epics.ADKafkaPlugin',
        description=
        'The configuration of the Kafka plugin for the FLIR camera.',
        kafkapv='labs-utg-test:Kfk1:',
        brokerpv='KafkaBrokerAddress_RBV',
        topicpv='KafkaTopic_RBV',
        sourcepv='SourceName_RBV',
        visibility=(),
    ),
    hama_kafka_plugin=device(
        'nicos_ess.devices.epics.ADKafkaPlugin',
        description=
        'The configuration of the Kafka plugin for the Hama camera.',
        kafkapv='Hama:Kfk1:',
        brokerpv='KafkaBrokerAddress_RBV',
        topicpv='KafkaTopic_RBV',
        sourcepv='SourceName_RBV',
        visibility=(),
    ),
    flir_camera=device(
        'nicos_ess.devices.epics.AreaDetector',
        description='The light tomography FLIR camera.',
        pv_root='labs-utg-test:cam1:',
        ad_kafka_plugin='flir_kafka_plugin',
        image_topic='ymir_camera',
        unit='images',
        brokers=['10.100.1.19:9092'],
        pollinterval=None,
        pva=True,
        monitor=True,
    ),
    hama_camera=device(
        'nicos_ess.devices.epics.AreaDetector',
        description='The light tomography Hama camera.',
        pv_root='Hama:cam1:',
        ad_kafka_plugin='hama_kafka_plugin',
        image_topic='ymir_camera',
        unit='images',
        brokers=['10.100.1.19:9092'],
        pollinterval=None,
        pva=True,
        monitor=True,
    ),
    flir_image_type=device(
        'nicos_ess.devices.epics.ImageType',
        description="Image type for the tomography setup.",
    ),
    hama_image_type=device(
        'nicos_ess.devices.epics.ImageType',
        description="Image type for the tomography setup.",
    ),
    area_detector_collector=device(
        'nicos_ess.devices.epics.AreaDetectorCollector',
        description='Area detector collector',
        images=['flir_camera', 'hama_camera'],
        liveinterval=1,
        pollinterval=1,
        unit='',
    ),
)

startupcode = '''
SetDetectors(area_detector_collector)
'''
