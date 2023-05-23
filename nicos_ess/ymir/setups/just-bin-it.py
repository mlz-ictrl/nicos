description = 'The just-bin-it histogrammer.'

devices = dict(
    det_image1=device(
        'nicos_ess.devices.datasources.just_bin_it.JustBinItImage',
        description='A just-bin-it image channel',
        hist_topic='ymir_visualisation',
        data_topic='freia_detector',
        brokers=['10.100.1.19:8093'],
        unit='evts',
        hist_type='2-D DET',
        det_width=64,
        det_height=200,
        det_range=(1, 12800),
    ),
    det_image2=device(
        'nicos_ess.devices.datasources.just_bin_it.JustBinItImage',
        description='A just-bin-it image channel',
        hist_topic='ymir_visualisation',
        data_topic='freia_detector',
        brokers=['10.100.1.19:8093'],
        unit='evts',
        hist_type='2-D TOF',
        det_width=64,
        det_height=200,
        det_range=(1, 12800),
        tof_range=(0, 1000000),
    ),
    det=device(
        'nicos_ess.devices.datasources.just_bin_it.JustBinItDetector',
        description='The just-bin-it histogrammer',
        brokers=['10.100.1.19:8093'],
        unit='',
        command_topic='ymir_jbi_commands',
        response_topic='ymir_jbi_responses',
        statustopic='ymir_jbi_heartbeat',
        images=['det_image1', 'det_image2'],
        hist_schema='hs01',
    ),
)

startupcode = '''
SetDetectors(det)
'''
