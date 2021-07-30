description = 'FOCUS standard devices'

mota = 'SQ:FOCUS:mota:'
motb = 'SQ:FOCUS:motb:'

devices = dict(
    mgo = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator Goniometer',
        motorpv = mota + 'MGO',
        errormsgpv = mota + 'MGO-MsgTxt',
        precision = 0.2,
    ),
    msl = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator SL',
        motorpv = mota + 'MSL',
        errormsgpv = mota + 'MSL-MsgTxt',
        precision = 0.2,
    ),
    mth = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator Rotation',
        motorpv = mota + 'MTH',
        errormsgpv = mota + 'MTH-MsgTxt',
        precision = 0.2,
    ),
    mtt = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator Two Theta',
        motorpv = mota + 'MTT',
        errormsgpv = mota + 'MTT-MsgTxt',
        precision = 0.2,
    ),
    mtx = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator X Translation',
        motorpv = mota + 'MTX',
        errormsgpv = mota + 'MTX-MsgTxt',
        precision = 0.2,
    ),
    mty = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator Y TRanlation',
        motorpv = mota + 'MTY',
        errormsgpv = mota + 'MTY-MsgTxt',
        precision = 0.2,
    ),
    m1cv = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator 1 vertical curvature',
        motorpv = motb + 'M1CV',
        errormsgpv = motb + 'M1CV-MsgTxt',
        precision = 0.2,
    ),
    m1ch = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator 1 horizontal curvature',
        motorpv = motb + 'M1CH',
        errormsgpv = motb + 'M1CH-MsgTxt',
        precision = 0.2,
    ),
    m2cv = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator 2 vertical curvature',
        motorpv = motb + 'M2CV',
        errormsgpv = motb + 'M2CV-MsgTxt',
        precision = 0.2,
    ),
    m2ch = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator 2 horizotal curvature',
        motorpv = motb + 'M2CH',
        errormsgpv = motb + 'M2CH-MsgTxt',
        precision = 0.2,
    ),
    mex = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Monochromator lift',
        motorpv = motb + 'MEX',
        errormsgpv = motb + 'MEX-MsgTxt',
        precision = 0.2,
    ),
    wavelength = device('nicos.devices.tas.mono.Monochromator',
        description = 'FOCUS monochromator wavelength',
        theta = 'mth',
        twotheta = 'mtt',
        dvalue = 3.355,
        unit = 'A',
        scatteringsense = 1,
        abslimits = (2.0, 6.0),
        crystalside = 1,
    ),
    ei = device('nicos.devices.tas.mono.Monochromator',
        description = 'FOCUS monochromator ei',
        theta = 'mth',
        twotheta = 'mtt',
        dvalue = 3.355,
        unit = 'meV',
        scatteringsense = 1,
        abslimits = (10, 100),
        crystalside = 1,
    ),
    mdif_lower = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = 'Lower Detector MDIF',
        commandpv = 'SQ:FOCUS:mdiflower' + '.AOUT',
        replypv = 'SQ:FOCUS:mdiflower' + '.AINP',
    ),
    mdif_middle = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = 'Middle Detector MDIF',
        commandpv = 'SQ:FOCUS:mdifmiddle' + '.AOUT',
        replypv = 'SQ:FOCUS:mdifmiddle' + '.AINP',
    ),
    mdif_upper = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = 'Upper Detector MDIF',
        commandpv = 'SQ:FOCUS:mdifupper' + '.AOUT',
        replypv = 'SQ:FOCUS:mdifupper' + '.AINP',
    ),
    mdif_f2d = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = '2D Detector MDIF',
        commandpv = 'SQ:FOCUS:mdif2d' + '.AOUT',
        replypv = 'SQ:FOCUS:mdif2d' + '.AINP',
    ),
    emmi = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = 'Direct communication with Emmenegger',
        commandpv = 'SQ:FOCUS:EMEG' + '.AOUT',
        replypv = 'SQ:FOCUS:EMEG' + '.AINP',
    ),
    el737direct = device('nicos_ess.devices.epics.extensions.EpicsCommandReply',
        epicstimeout = 3.0,
        description = 'Direct communication with EL737 counter box',
        commandpv = 'SQ:FOCUS:cter' + '.AOUT',
        replypv = 'SQ:FOCUS:cter' + '.AINP',
    ),
    col = device('nicos_sinq.devices.s5_switch.S5Switch',
        description = 'Switch for the radial collimator',
        epicstimeout = 3.0,
        readpv = 'SQ:FOCUS:SPS1:DigitalInput',
        commandpv = 'SQ:FOCUS:SPS1:Push',
        byte = 10,
        mapping = {
            'OFF': False,
            'ON': True
        },
        bit = 0,
        commandstr = 'S0000',
    ),
    fbox = device('nicos_sinq.devices.s5_switch.S5Bit',
        description = 'Status of the flight box',
        byte = 12,
        bit = 2,
        readpv = 'SQ:FOCUS:SPS1:DigitalInput',
        epicstimeout = 3.
    ),
    fermidist = device('nicos.devices.generic.manual.ManualMove',
        description = 'Distance sample - fermi chopper',
        unit = 'mm',
        abslimits = (2500, 5000),
        default = 3000
    ),
    sampledist = device('nicos.devices.generic.manual.ManualMove',
        description = 'Distance sample - detector',
        unit = 'mm',
        abslimits = (0, 2500),
        default = 2000
    ),
)

startupcode = """
mdif_lower.execute('RMT 1')
mdif_lower.execute('ECHO 0')
mdif_middle.execute('RMT 1')
mdif_middle.execute('ECHO 0')
mdif_upper.execute('RMT 1')
mdif_upper.execute('ECHO 0')
mdif_f2d.execute('RMT 1')
mdif_f2d.execute('ECHO 0')
"""