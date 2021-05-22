description = 'Multiblade detector'

sysconfig = dict(datasinks = ['jbi_liveview'],)

display_order = 28

devices = dict(
    det_image = device(
        'nicos_ess.devices.datasources.just_bin_it.JustBinItImage',
        description = 'Detector image channel',
        hist_topic = 'AMOR_histograms',
        data_topic = 'FREIA_detector',
        brokers = configdata('config.KAFKA_BROKERS'),
        unit = 'evts',
        hist_type = '2-D DET',
        det_width = 32,
        det_height = 160,
        det_range = (0, 32*160),
        lowlevel= True
    ),
    proton_charge = device(
        'nicos_sinq.devices.epics.proton_counter.SINQProtonCharge',
        description = 'Proton charge monitor',
        readpv = 'SQ:AMOR:current:BEAMINT',
        pvprefix = 'SQ:AMOR:current:',
        unit = 'uC',
        type = 'counter',
        fmtstr = '%3.3f',
    ),
    det = device('nicos_ess.devices.datasources.just_bin_it.JustBinItDetector',
        description = 'The just-bin-it histogrammer',
        brokers = configdata('config.KAFKA_BROKERS'),
        unit = '',
        command_topic = 'AMOR_histCommands',
        response_topic = 'AMOR_histResponse',
        images = ['det_image'],
        monitors = ['proton_charge'],
    ),
    jbi_liveview = device('nicos.devices.datasinks.LiveViewSink',
    ),
)

startupcode = '''
SetDetectors(det)
'''
