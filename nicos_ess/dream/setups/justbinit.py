description = 'JustBinIt histogrammer.'

devices = dict(
    det_image1=device(
        'nicos_ess.devices.datasources.just_bin_it.JustBinItImage',
        description='A just-bin-it image channel',
        hist_topic='hist_topic_1',
        data_topic='fake_events',
        brokers=['localhost:9092'],
        source='just-bin-it',
        unit='evts',
        hist_type='2-D TOF',
        det_range=(0, 10000),
        ),
    det_image2=device(
        'nicos_ess.devices.datasources.just_bin_it.JustBinItImage',
        description='A just-bin-it image channel',
        hist_topic='hist_topic_2',
        data_topic='fake_events',
        brokers=['localhost:9092'],
        source='just-bin-it',
        unit='evts',
        hist_type='1-D TOF',
        det_range=(0, 10000),
    ),
    det=device('nicos_ess.devices.datasources.just_bin_it.JustBinItDetector',
        description='Just Bin it histogrammer',
        brokers=['localhost:9092'],
        unit='',
        command_topic='hist_commands',
        response_topic='response_topic',
        images=['det_image1', 'det_image2'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
