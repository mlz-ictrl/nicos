description = 'The area detector for YMIR'
pv_root = 'YMIR-CamSy1:FLIR-Cam:'

devices = dict(
    flir_kafka_plugin=device(
        'nicos_ess.devices.epics.ADKafkaPlugin',
        description='The configuration of the Kafka plugin for the FLIR camera.',
        kafkapv='labs-utg-test:Kfk1:',
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
    ),
    area_detector_collector=device(
        'nicos_ess.devices.epics.AreaDetectorCollector',
        description='Area detector collector',
        images=['flir_camera']
    ),
    flir_image_type=device(
        'nicos_ess.devices.epics.ImageType',
        description="Image type for the tomography setup.",
    ),
)
