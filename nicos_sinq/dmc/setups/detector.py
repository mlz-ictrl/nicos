description = 'Setup for the MesyDAQ detector'

pvprefix = 'SQ:DMC-DAQ:SG'

channels = ['raw_counts', 'm1', 'm2', 'proton']

devices = dict(
    hipa_current = device(
        'nicos.devices.epics.pva.epics_devices.EpicsReadable',
        description = "Proton Current",
        readpv = "MHC6:IST:2",
        monitor = True,
    ),

    # Motors
    a4 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Detector angle (s2t)',
        motorpv = 'SQ:DMC:turboPmac1:A4',
        errormsgpv = 'SQ:DMC:turboPmac1:A4-MsgTxt',
        can_disable = True,
    ),

    # Detector Technical Measures
    dropped_packets = device(
        'nicos.devices.epics.pva.epics_devices.EpicsReadable',
        description = "Number of packets that didn't arrive at DAQ PC",
        readpv = pvprefix + ':UDP_DROPPED',
        monitor = True,
    ),
    udp_queue = device(
        'nicos.devices.epics.pva.epics_devices.EpicsReadable',
        description = "Max % that queue was filled during processing",
        readpv = pvprefix + ':UDP_WATERMARK',
        monitor = True,
    ),
    normalised_queue = device(
        'nicos.devices.epics.pva.epics_devices.EpicsReadable',
        description = "Max % that queue was filled during processing",
        readpv = pvprefix + ':NORMALISED_WATERMARK',
        monitor = True,
    ),
    process_queue = device(
        'nicos.devices.epics.pva.epics_devices.EpicsReadable',
        description = "Max % that queue was filled during processing",
        readpv = pvprefix + ':SORTED_WATERMARK',
        monitor = True,
    ),
    correlation_unit = device(
        'nicos.devices.epics.pva.epics_devices.EpicsMappedMoveable',
        description = "Enable or Disable Detector Electronics",
        readpv = pvprefix + ':Enable_RBV',
        writepv = pvprefix + ':Enable',
        monitor = True,
    ),

    # Detector Specific
    det_timer = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQTime',
        daqpvprefix = pvprefix,
    ),
    raw_counts = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Detector counts',
        daqpvprefix = pvprefix,
        channel = 5,
        type = 'monitor',
    ),
    m1 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Reference Monitor of SANS-LLB before the Shutter',
        daqpvprefix = pvprefix,
        channel = 1,
        type = 'monitor',
    ),
    m2 = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Monitor after Monochromator',
        daqpvprefix = pvprefix,
        channel = 2,
        type = 'monitor',
    ),
    proton = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Proton Beam Signal (real-time)',
        daqpvprefix = pvprefix,
        channel = 3,
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
    hardware_preset = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQPreset',
        description = 'In-hardware Time/Count Preset',
        daqpvprefix = pvprefix,
        channels = channels,
        time_channel = 'det_timer',
    ),
    det = device(
        'nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector Device',
        unit = '',
        timers = ['det_timer'],
        monitors = ['hardware_preset'] + channels,
        images = ['det_image'],
        liveinterval = 1,
    ),
)

startupcode = '''
SetDetectors(det)
'''
