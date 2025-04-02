description = 'Slit 2 devices in the SINQ AMOR.'

display_order = 45

pvprefix = 'SQ:AMOR:masterMacs1:'

devices = dict(
    d2t = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 top blade',
        motorpv = pvprefix + 'd2t',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d2b = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 bottom blade',
        motorpv = pvprefix + 'd2b',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d2l = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 left blade',
        motorpv = pvprefix + 'd2l',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d2r = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 right blade',
        motorpv = pvprefix + 'd2r',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d2z = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Slit 2 z position',
        motorpv = pvprefix + 'd2z',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    slit2 = device('nicos.devices.generic.slit.Slit',
        description = 'Slit 2 with left, right, bottom and top motors',
        opmode = '4blades',
        left = 'd2l',
        right = 'd2r',
        top = 'd2t',
        bottom = 'd2b',
        visibility = (),
    ),
)
