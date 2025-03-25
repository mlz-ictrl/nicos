description = 'Monochromator slit devices'

display_order = 30

pvmcu = 'SQ:CAMEA:turboPmac2:'

devices = dict(
    mst = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator slit top',
        motorpv = pvmcu + 'mst',
    ),
    msb = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator slit bottom',
        motorpv = pvmcu + 'msb',
    ),
    msr = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Monochromator slit right',
        motorpv = pvmcu + 'msr',
    ),
    msl = device('nicos_sinq.devices.epics.motor.SinqMotor',
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
        visibility = (),
    ),
    mslit_height = device('nicos_sinq.amor.devices.slit.SlitOpening',
        description = 'Detector Slit opening controller',
        slit = 'mslit'
    ),
    mslit_width = device('nicos.devices.generic.slit.WidthSlitAxis',
        description = 'Detector Slit width controller',
        slit = 'mslit',
        unit = 'mm',
    ),
)
