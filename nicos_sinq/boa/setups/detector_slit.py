description = 'BOA Detector Slit'

pvprefix = 'SQ:BOA:sld:'

devices = dict(
    dsl = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Detector Slit left motor',
        motorpv = pvprefix + 'DSL',
        errormsgpv = pvprefix + 'DSL-MsgTxt',
    ),
    dsr = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Detector Slit right motor',
        motorpv = pvprefix + 'DSR',
        errormsgpv = pvprefix + 'DSR-MsgTxt',
    ),
    dsb = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Detector Slit bottom motor',
        motorpv = pvprefix + 'DSB',
        errormsgpv = pvprefix + 'DSB-MsgTxt',
    ),
    dst = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Detector Slit top motor',
        motorpv = pvprefix + 'DST',
        errormsgpv = pvprefix + 'DST-MsgTxt',
    ),
    dslit = device('nicos.devices.generic.slit.Slit',
        description = 'Detector Slit with left, right, bottom and '
        'top motors',
        opmode = '4blades',
        left = 'dsl',
        right = 'dsr',
        top = 'dst',
        bottom = 'dsb',
        lowlevel = True
    ),
    dslit_opening = device('nicos_sinq.amor.devices.slit.SlitOpening',
        description = 'Detector Slit opening controller',
        slit = 'dslit'
    ),
    dslit_width = device('nicos.devices.generic.slit.WidthSlitAxis',
        description = 'Detector Slit width controller',
        slit = 'dslit',
        unit = 'mm',
    ),
)
