description = 'BOA Detector Slit'

pvprefix = 'SQ:BOA:sld:'

devices = dict(
    dsl = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Detector Slit left motor',
        motorpv = pvprefix + 'DSL',
        errormsgpv = pvprefix + 'DSL-MsgTxt',
        precision = 0.00375
    ),
    dsr = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Detector Slit right motor',
        motorpv = pvprefix + 'DSR',
        errormsgpv = pvprefix + 'DSR-MsgTxt',
        precision = 0.00375
    ),
    dsb = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Detector Slit bottom motor',
        motorpv = pvprefix + 'DSB',
        errormsgpv = pvprefix + 'DSB-MsgTxt',
        precision = 0.00375
    ),
    dst = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Detector Slit top motor',
        motorpv = pvprefix + 'DST',
        errormsgpv = pvprefix + 'DST-MsgTxt',
        precision = 0.00375
    ),
    dslit = device('nicos.devices.generic.slit.Slit',
        description = 'Detector Slit with left, right, bottom and '
        'top motors',
        opmode = '4blades',
        left = 'dsl',
        right = 'dsr',
        top = 'dst',
        bottom = 'dsb',
        visibility = (),
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
