description = 'Monochromator slit devices'

display_order = 30

pvmcu = 'SQ:CAMEA:turboPmac2:'

devices = dict(
    mst = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Monochromator slit top',
        motorpv = pvmcu + 'mst',
    ),
    msb = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Monochromator slit bottom',
        motorpv = pvmcu + 'msb',
    ),
    msr = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Monochromator slit right',
        motorpv = pvmcu + 'msr',
    ),
    msl = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Monochromator slit left',
        motorpv = pvmcu + 'msl',
    ),
    mslit = device('nicos.devices.generic.slit.Slit',
        description = 'Monochromator slit with left, right, bottom and '
        'top motors',
        opmode = '4blades',
        left = 'msl',
        right = 'msr',
        top = 'mst',
        bottom = 'msb',
        coordinates = 'opposite',
        min_opening = 0.2, # Should not be changed without consulting Electronics support
    ),
    mslit_height = device('nicos.devices.generic.slit.HeightSlitAxis',
        description = 'Detector Slit height controller',
        slit = 'mslit',
        unit = 'mm',
    ),
    mslit_width = device('nicos.devices.generic.slit.WidthSlitAxis',
        description = 'Detector Slit width controller',
        slit = 'mslit',
        unit = 'mm',
    ),
)
