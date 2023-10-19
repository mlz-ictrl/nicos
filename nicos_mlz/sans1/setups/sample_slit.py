description = 'collimation slit'

group = 'lowlevel'

tango_base = 'tango://hw.sans1.frm2.tum.de:10000/sample/slit/'

devices = dict(
    s_slit_top = device('nicos.devices.entangle.Motor',
        description = 'collimation slit top axis',
        tangodevice = tango_base + 'top',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    s_slit_bottom = device('nicos.devices.entangle.Motor',
        description = 'collimation slit bottom axis',
        tangodevice = tango_base + 'bottom',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    s_slit_left = device('nicos.devices.entangle.Motor',
        description = 'collimation slit left axis',
        tangodevice = tango_base + 'left',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    s_slit_right = device('nicos.devices.entangle.Motor',
        description = 'collimation slit right axis',
        tangodevice = tango_base + 'right',
        abslimits = (0, 25),
        precision = 0.05,
    ),
    s_slit = device('nicos.devices.generic.Slit',
        description = 'Sample slit',
        top = 's_slit_top',
        bottom = 's_slit_bottom',
        left = 's_slit_left',
        right = 's_slit_right',
        opmode = 'centered',
        coordinates = 'opposite',
        pollinterval = 5,
        maxage = 12,
    ),
)
