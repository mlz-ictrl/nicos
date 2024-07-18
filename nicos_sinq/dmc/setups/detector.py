description = 'Setup for the MesyDAQ detector'

pvprefix = 'SQ:DMC:counter'

sysconfig = dict(datasinks = ['jbi_liveview'])

devices = dict(
    a4 = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Detector angle (s2t)',
        motorpv = 'SQ:DMC:mcu1:A4',
        errormsgpv = 'SQ:DMC:mcu1:A4-MsgTxt',
        can_disable = True,
    ),
    det_timer = device('nicos.devices.generic.VirtualTimer',
        description = 'Detector timer',
    ),
    m1 = device('nicos_sinq.devices.counters.KafkaCounter',
        description = 'consume monitors events from kafka topic',
        brokers = configdata('config.KAFKA_BROKERS'),
        topic = configdata('config.BEAM_MONITOR_TOPIC'),
        source = 'monitor1',
        type = 'monitor',
    ),
    m2 = device('nicos_sinq.devices.counters.KafkaCounter',
        description = 'consume monitors events from kafka topic',
        brokers = configdata('config.KAFKA_BROKERS'),
        topic = configdata('config.BEAM_MONITOR_TOPIC'),
        source = 'monitor2',
        type = 'monitor',
    ),
    det_image = device('nicos_sinq.devices.just_bin_it.JustBinItImage',
        description = 'Detector image channel',
        hist_topic = configdata('config.JUST_BIN_IT_HISTOGRAMS_TOPIC'),
        data_topic = configdata('config.JUST_BIN_IT_DATA_TOPIC'),
        command_topic = configdata('config.JUST_BIN_IT_COMMANDS_TOPIC'),
        brokers = configdata('config.KAFKA_BROKERS'),
        unit = 'evts',
        hist_type = '2-D DET',
        det_width = 128,
        det_height = 128 * 9,
        det_range = (0, 128 * 128 * 9),
        rotation = 0,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'The just-bin-it histogrammer',
        unit = '',
        timers = ['det_timer'],
        images = ['det_image'],
        monitors = ['m1', 'm2'],
    ),
    jbi_liveview = device('nicos.devices.datasinks.LiveViewSink',
    ),
)

startupcode = '''
SetDetectors(det)
'''
