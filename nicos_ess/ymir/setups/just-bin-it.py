description = 'The just-bin-it histogrammer.'

devices = dict(
    det=device('nicos_ess.devices.datasources.just_bin_it.JustBinItDetector',
               description='The just-bin-it histogrammer',
               hist_topic='hist-topic', data_topic='FREIA_detector',
               brokers=['172.30.242.20:9092'], unit='evts',
               command_topic='hist_commands', response_topic='hist_responses',
               hist_type='2-D DET', det_width=32, det_height=192,
               det_range=(1, 6144)),
)

startupcode = '''
SetDetectors(det)
'''
