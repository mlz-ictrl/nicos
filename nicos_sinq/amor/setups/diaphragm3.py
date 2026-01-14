description = 'Slit 3 devices in the SINQ AMOR.'

display_order = 60

pvprefix = 'SQ:AMOR:masterMacs1:'

devices = dict(
    d3t = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 3 top blade',
        motorpv = pvprefix + 'd3t',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d3b = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 3 bottom blade',
        motorpv = pvprefix + 'd3b',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d3l = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 3 left blade',
        motorpv = pvprefix + 'd3l',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d3r = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 3 right blade',
        motorpv = pvprefix + 'd3r',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    d3z = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Slit 3 z position',
        motorpv = pvprefix + 'd3z',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    slit3 = device('nicos.devices.generic.slit.Slit',
        description = 'Slit 3 with left, right, bottom and top motors',
        opmode = '4blades',
        left = 'd3l',
        right = 'd3r',
        top = 'd3t',
        bottom = 'd3b',
        visibility = (),
    ),
)
