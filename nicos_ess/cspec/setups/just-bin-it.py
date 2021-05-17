description = 'The just-bin-it histogrammer.'

devices = dict(
    det_image1=device(
        'nicos_ess.devices.datasources.just_bin_it.JustBinItImage',
        description='A just-bin-it image channel',
        hist_topic='cspec_jbi_1',
        data_topic='CSPEC_detector',
        brokers=['172.30.242.20:9092'],
        unit='evts',
        hist_type='2-D DET',
        det_width=32,
        det_height=192,
        det_range=(1, 6144),
        ),
    det_image2=device(
        'nicos_ess.devices.datasources.just_bin_it.JustBinItImage',
        description='A just-bin-it image channel',
        hist_topic='cspec_jbi_2',
        data_topic='CSPEC_detector',
        brokers=['172.30.242.20:9092'],
        unit='evts',
        hist_type='2-D TOF',
        det_width=32,
        det_height=192,
    ),
    det=device('nicos_ess.devices.datasources.just_bin_it.JustBinItDetector',
        description='The just-bin-it histogrammer',
        brokers=['172.30.242.20:9092'],
        unit='',
        command_topic='cspec_jbi_commands',
        response_topic='cspec_jbi_responses',
        images=['det_image1', 'det_image2'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
