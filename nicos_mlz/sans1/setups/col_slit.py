description = 'collimation slit'

group = 'lowlevel'

tango_base = 'tango://hw.sans1.frm2.tum.de:10000/col/slit/'

devices = dict(
    slit_top = device('nicos.devices.entangle.Motor',
        description = 'collimation slit top axis',
        tangodevice = tango_base + 'top',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    slit_bottom = device('nicos.devices.entangle.Motor',
        description = 'collimation slit bottom axis',
        tangodevice = tango_base + 'bottom',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    slit_left = device('nicos.devices.entangle.Motor',
        description = 'collimation slit left axis',
        tangodevice = tango_base + 'left',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    slit_right = device('nicos.devices.entangle.Motor',
        description = 'collimation slit right axis',
        tangodevice = tango_base + 'right',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    slit = device('nicos.devices.generic.Slit',
        description = 'Collimation slit',
        top = 'slit_top',
        bottom = 'slit_bottom',
        left = 'slit_left',
        right = 'slit_right',
        opmode = 'centered',
        coordinates = 'opposite',
        pollinterval = 5,
        maxage = 12,
    ),
)
