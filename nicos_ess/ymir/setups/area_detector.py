description = 'The area detector for YMIR'

devices = dict(
    ad_kafka_plugin=device(
        'nicos_ess.devices.epics.ADKafkaPlugin',
        description='The configuration of the area detector Kafka plugin',
        kafkapv='labs-utg-test:Kfk1:',
        brokerpv='KafkaBrokerAddress_RBV',
        topicpv='KafkaTopic_RBV',
        sourcepv='SourceName_RBV',
    ),
    area_detector=device(
        'nicos_ess.devices.epics.AreaDetector',
        description='The light tomography FLIR camera.',
        pv_root='labs-utg-test:cam1:',
        ad_kafka_plugin='ad_kafka_plugin',
    ),
    area_detector_collector=device(
        'nicos_ess.devices.epics.AreaDetectorCollector',
        description='Area detector collector',
        images=['area_detector']
    )
)
