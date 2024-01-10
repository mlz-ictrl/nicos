description = 'Multiblade detector'

display_order = 15

excludes = ['detector']

sysconfig = dict(datasinks = ['jbi_liveview'],)

sumpv = 'SQ:AMOR:sumi:'

devices = dict(
    det_timer = device('nicos.devices.generic.VirtualTimer',
        description = 'Detector timer',
        unit = 's',
    ),
    proton_monitor = device('nicos_sinq.devices.epics.proton_counter.SINQProtonMonitor',
        description = 'Proton monitor',
        pvprefix = sumpv,
        unit = 'uA',
        type = 'monitor',
    ),
    m1 = device('nicos_sinq.devices.counters.KafkaCounter',
        description = 'consume monitors events from kafka topic',
        brokers = configdata('config.KAFKA_BROKERS'),
        topic = 'amor_beam_monitor',
        source = 'ttlmon0',
        type = 'monitor',
    ),
    det_image = device('nicos_sinq.devices.just_bin_it.JustBinItImage',
        description = 'Detector image channel',
        hist_topic = 'AMOR_histograms',
        data_topic = 'amor_detector',
        command_topic = 'AMOR_histCommands',
        brokers = configdata('config.KAFKA_BROKERS'),
        unit = 'evts',
        hist_type = '2-D DET',
        det_width = 32,
        det_height = 448,
        det_range = (0, 32 * 448),
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'The just-bin-it histogrammer',
        unit = '',
        timers = ['det_timer'],
        monitors = ['m1', 'proton_monitor'],
        images = ['det_image'],
    ),
    jbi_liveview = device('nicos.devices.datasinks.LiveViewSink',
    ),
)

startupcode = '''
SetDetectors(det)
'''
