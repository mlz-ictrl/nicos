description = 'Devices for the Detector'

group = 'basic'

includes = ['hm_config_strobo', 'attenuator', 'velocity_selector', 'beamstop', 'collimator_s7', 'sample', 'shutter', 'asyncontroller']
exludes = ['detector']

pvprefix = 'SQ:SANS:motb:'
pvdprefix = 'SQ:SANS:counter'

devices = dict(
    detx = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Detector X Translation',
        motorpv = pvprefix + 'detX',
        errormsgpv = pvprefix + 'detX-MsgTxt',
        precision = 0.5,
    ),
    dety = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Detector Y Translation',
        motorpv = pvprefix + 'detY',
        errormsgpv = pvprefix + 'detY-MsgTxt',
        precision = 0.2,
    ),
    detphi = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Detector Rotation',
        motorpv = pvprefix + 'phi',
        errormsgpv = pvprefix + 'phi-MsgTxt',
        precision = 0.2,
    ),
    timepreset = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = pvdprefix + '.TP',
        presetpv = pvdprefix + '.TP',
    ),
    elapsedtime = device('nicos_sinq.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = pvdprefix + '.T',
    ),
    monitorpreset = device('nicos_sinq.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = pvdprefix + '.PR2',
        presetpv = pvdprefix + '.PR2',
    ),
    monitor1 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'First scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S2',
    ),
    monitor2 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Second scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S3',
    ),
    monitor3 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Third scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S4',
    ),
    monitor4 = device('nicos_sinq.devices.epics.detector'
        '.EpicsCounterPassiveChannel',
        description = 'Third scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S5',
    ),
    monitor5 = device('nicos_sinq.devices.epics.detector'
        '.EpicsCounterPassiveChannel',
        description = 'Third scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S6',
    ),
    monitor6 = device('nicos_sinq.devices.epics.detector'
        '.EpicsCounterPassiveChannel',
        description = 'Third scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S7',
    ),
    monitor7 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Seventh scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S8',
    ),
    monitor8 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Eigth scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S2',
    ),
    protoncount = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Fourth scalar counter channel',
        type = 'monitor',
        readpv = pvdprefix + '.S5',
    ),
    histogrammer = device('nicos_sinq.devices.sinqhm.channel.HistogramMemoryChannel',
        description = "Histogram Memory Channel",
        connector = 'hm_connector'
    ),
    sans_detector = device('nicos_sinq.sans.devices.sanschannel.StroboHistogramImageChannel',
        description = "Image channel for area detector",
        visibility = (),
        bank = 'hm_bank0',
        dimensions = {
            'x': 128,
            'y': 128
        },
        connector = 'hm_connector',
        tof_axis = 'hm_ax_tof',
    ),
    sans_slice = device('nicos_sinq.devices.channel.SelectSliceImageChannel',
        description = 'Slice selector',
        data_channel = 'sans_detector'
    ),
    sansdet = device('nicos_sinq.devices.detector.SinqDetector',
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv = pvdprefix + '.CNT',
        pausepv = pvdprefix + ':Pause',
        statuspv = pvdprefix + ':Status',
        errormsgpv = pvdprefix + ':MsgTxt',
        thresholdpv = pvdprefix + ':Threshold',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = [
            'monitor1', 'protoncount', 'monitor2', 'monitor3', 'monitor4',
            'monitor5', 'monitor6', 'monitor7', 'monitor8'
        ],
        images = ['sans_detector', 'sans_slice'],
        others = ['histogrammer'],
        liveinterval = 7,
        saveintervals = [60]
    )
)
startupcode = """
hm_configurator.updateConfig()
SetDetectors(sansdet)
"""
