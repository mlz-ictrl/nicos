description = 'Standard EIGER devices minus the monochromator'

mcu2prefix = 'SQ:EIGER:turboPmac2:'
mcu3prefix = 'SQ:EIGER:turboPmac3:'
mcu4prefix = 'SQ:EIGER:turboPmac4:'
cterprefix = 'SQ:EIGER:counter'

devices = dict(
    d1l = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 1 left',
        motorpv = mcu2prefix + 'd1l',
    ),
    d1r = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 1 right',
        motorpv = mcu2prefix + 'd1r',
    ),
    vsl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Virtual source left',
        motorpv = mcu2prefix + 'vsl',
    ),
    vsr = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Virtual source right',
        motorpv = mcu2prefix + 'vsr',
    ),
    msl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample slit left',
        motorpv = mcu2prefix + 'msl',
    ),
    msr = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample slit right',
        motorpv = mcu2prefix + 'msr',
    ),
    msb = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample slit bottom',
        motorpv = mcu4prefix + 'msb',
    ),
    mst = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample slit top',
        motorpv = mcu4prefix + 'mst',
    ),
    a3_raw = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample rotation',
        motorpv = mcu3prefix + 'a3',
    ),
    a3 = device('nicos.core.device.DeviceAlias',
        description = 'Alias for a3',
        alias = 'a3_raw',
        devclass = 'nicos.core.device.Moveable'
    ),
    sslit = device('nicos.devices.generic.slit.Slit',
        description = 'Sample slit with left, right, bottom and '
        'top motors',
        opmode = 'centered',
        left = 'msl',
        right = 'msr',
        top = 'mst',
        bottom = 'msb',
        coordinates = 'opposite',
        parallel_ref = True,
    ),
    sslit_height = device('nicos.core.device.DeviceAlias',
        description = 'Sample slit height controller',
        alias = 'sslit.height',
        devclass = 'nicos.devices.generic.slit.HeightSlitAxis'
    ),
    sslit_width = device('nicos.core.device.DeviceAlias',
        description = 'Sample slit width controller',
        alias = 'sslit.width',
        devclass = 'nicos.devices.generic.slit.WidthSlitAxis'
    ),
    a4 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample two theta',
        motorpv = mcu3prefix + 'a4',
    ),
    sgl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample lower tilt',
        motorpv = mcu3prefix + 'sgl',
    ),
    sgu = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample upper tilt',
        motorpv = mcu3prefix + 'sgu',
    ),
    a5 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Analyser rotation',
        motorpv = mcu4prefix + 'a5',
    ),
    a6_raw = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Analyser rotation',
        motorpv = mcu4prefix + 'a6',
        visibility = {'metadata'},
    ),
    a6 = device('nicos_sinq.eiger.devices.a6motor.A6Motor',
        description = 'Analyser two theta',
        raw_motor = 'a6_raw',
        wait_period = 7,
        precision = .02,
    ),
    ach = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Analyser horizontal curvature',
        motorpv = mcu4prefix + 'ach',
    ),
    atl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Analyser lower translation',
        motorpv = mcu4prefix + 'atl',
    ),
    atu = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Analyser upper translation',
        motorpv = mcu4prefix + 'atu',
    ),
    ag = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Analyser goniometer',
        motorpv = mcu4prefix + 'ag',
    ),
    timepreset = device('nicos_sinq.devices.epics.detector.EpicsTimerActiveChannel',
        description = 'Used to set and view time preset',
        unit = 'sec',
        readpv = cterprefix + '.TP',
        presetpv = cterprefix + '.TP',
    ),
    elapsedtime = device('nicos_sinq.devices.epics.detector.EpicsTimerPassiveChannel',
        description = 'Used to view elapsed time while counting',
        unit = 'sec',
        readpv = cterprefix + '.T',
    ),
    monitorpreset = device('nicos_sinq.devices.epics.detector.EpicsCounterActiveChannel',
        description = 'Used to set and view monitor preset',
        type = 'monitor',
        readpv = cterprefix + '.PR2',
        presetpv = cterprefix + '.PR2',
    ),
    ctr1 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'The real neutron counter',
        type = 'counter',
        readpv = cterprefix + '.S3',
    ),
    mon1 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'First scalar counter channel',
        type = 'monitor',
        readpv = cterprefix + '.S2',
    ),
    mon2 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Second scalar counter channel',
        type = 'monitor',
        readpv = cterprefix + '.S4',
    ),
    mon3 = device('nicos_sinq.devices.epics.detector.EpicsCounterPassiveChannel',
        description = 'Fourth scalar counter channel',
        type = 'monitor',
        readpv = cterprefix + '.S5',
    ),
    counter = device('nicos_sinq.devices.detector.SinqDetector',
        description = 'EL737 counter box that counts neutrons and '
        'starts streaming events',
        startpv = cterprefix + '.CNT',
        pausepv = cterprefix + ':Pause',
        statuspv = cterprefix + ':Status',
        errormsgpv = cterprefix + ':MsgTxt',
        thresholdpv = cterprefix + ':Threshold',
        thresholdcounterpv = cterprefix + ':ThresholdCounter',
        monitorpreset = 'monitorpreset',
        timepreset = 'timepreset',
        timers = ['elapsedtime'],
        monitors = [
            'ctr1',
            'mon1',
            'mon2',
            'mon3',
        ],
        liveinterval = 7,
        saveintervals = [60]
    ),
    ana = device('nicos_sinq.devices.mono.TasAnalyser',
        description = 'EIGER analyser',
        theta = 'a5',
        twotheta = 'a6',
        material = 'PG',
        reflection = (0, 0, 2),
        dvalue = 3.354,
        scatteringsense = 1,
        crystalside = 1,
        unit = 'meV',
        focmode = 'horizontal',
        hfocuspars = [0.21, 3.99],
        abslimits = [2.75, 80],
        focush = 'ach'
    ),
    ef = device('nicos.core.device.DeviceAlias',
        description = 'Alias for driving the analyser',
        alias = 'ana',
    ),
)

startupcode = """
SetDetectors(counter)
"""
