description = 'BOA Slit 1'

pvprefix = 'SQ:BOA:sl1:'

devices = dict(
    sal = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Slit 1 left motor',
        motorpv = pvprefix + 'SAL',
        errormsgpv = pvprefix + 'SAL-MsgTxt',
        precision = 0.000625
    ),
    sar = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Slit 1 right motor',
        motorpv = pvprefix + 'SAR',
        errormsgpv = pvprefix + 'SAR-MsgTxt',
        precision = 0.000625
    ),
    sab = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Slit 1 bottom motor',
        motorpv = pvprefix + 'SAB',
        errormsgpv = pvprefix + 'SAB-MsgTxt',
        precision = 0.000625
    ),
    sat = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Slit 1 top motor',
        motorpv = pvprefix + 'SAT',
        errormsgpv = pvprefix + 'SAT-MsgTxt',
        precision = 0.000625
    ),
    slit1 = device('nicos.devices.generic.slit.Slit',
        description = 'Slit 1 with left, right, bottom and top motors',
        opmode = '4blades',
        left = 'sal',
        right = 'sar',
        top = 'sat',
        bottom = 'sab',
        visibility = (),
    ),
    slit1_height = device('nicos_sinq.amor.devices.slit.SlitOpening',
        description = 'Slit 1 height controller',
        slit = 'slit1'
    ),
    slit1_width = device('nicos.devices.generic.slit.WidthSlitAxis',
        description = 'Slit 1 width controller',
        slit = 'slit1',
        unit = 'mm',
    ),
)
