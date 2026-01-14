description = 'Slit 1 devices in the SINQ AMOR.'

display_order = 35

pvprefix = 'SQ:AMOR:turboPmac4:'

devices = dict(
    d1t = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 1 top blade',
        motorpv = pvprefix + 'd1t',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d1b = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 1 bottom blade',
        motorpv = pvprefix + 'd1b',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d1l = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 1 left blade',
        motorpv = pvprefix + 'd1l',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d1r = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 1 right blade',
        motorpv = pvprefix + 'd1r',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    slit1 = device('nicos.devices.generic.slit.Slit',
        description = 'Slit 1 with left, right, bottom and top motors',
        opmode = '4blades_opposite',
        left = 'd1l',
        right = 'd1r',
        top = 'd1t',
        bottom = 'd1b',
        visibility = ('metadata', 'namespace'),
    ),
)
