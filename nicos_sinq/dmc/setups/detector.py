description = 'DMC Mesytech detector'

sysconfig = dict(datasinks = ['jbi_liveview'],)

excludes = ['el737', 'andorccd']

devices = dict(
    a4=device('nicos_ess.devices.epics.motor.EpicsMotor',
               epicstimeout=3.0,
               description='Detector angle (s2t)',
               motorpv='SQ:DMC:mcu2:S2T',
               errormsgpv='SQ:DMC:mcu2:S2T-MsgTxt',
               ),
    det_image = device('nicos_ess.devices.datasources.just_bin_it.JustBinItImage',
        description = 'Detector image channel',
        hist_topic = configdata('config.JUST_BIN_IT_HISTOGRAMS_TOPIC'),
        data_topic =configdata('config.JUST_BIN_IT_DATA_TOPIC'),
        brokers = configdata('config.KAFKA_BROKERS'),
        unit = 'evts',
        hist_type = '2-D DET',
        det_width = 128,
        det_height = 128*8,
        det_range = (0, 128*128*8)
    ),
    jbi_liveview = device('nicos.devices.datasinks.LiveViewSink',
    ),
    proton_current = device('nicos.devices.epics.EpicsReadable',
        description = 'Proton current monitor',
        readpv = 'MHC6:IST:2',
        unit = 'uA',
        fmtstr = '%3.3f',
    ),
    proton_charge = device('nicos_sinq.devices.epics.proton_counter.SINQProtonCharge',
        description='Proton charge monitor',
        readpv='SQ:DMC:current:ACCINT',
        pvprefix='SQ:DMC:current:',
        unit = 'uC',
        type = 'counter',
        fmtstr = '%3.3f',
    ),
    monitor = device('nicos_ess.devices.epics.detector.EpicsCounterActiveChannel',
        epicstimeout=3.0,
        description='Scalar counter channel',
        type='monitor',
        readpv='SQ:DMC:monitor:counts',
        presetpv = 'SQ:DMC:monitor:target'
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        lowlevel = True,
    ),
    det = device('nicos_ess.devices.datasources.just_bin_it.JustBinItDetector',
        description = 'The just-bin-it histogrammer',
        brokers = configdata('config.KAFKA_BROKERS'),
        unit = '',
        command_topic = configdata('config.JUST_BIN_IT_COMMANDS_TOPIC'),
        response_topic = configdata('config.JUST_BIN_IT_RESPONSES_TOPIC'),
        images = ['det_image'],
        monitors = ['monitor'],
        timers = ['timer'],
        counters = ['proton_charge'],
    ),

)

start = """
SetDetectors(det)
"""

