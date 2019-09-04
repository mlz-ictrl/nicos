description = 'Small Beam Limiter in Experimental Chamber 1'

group = 'optional'

excludes = ['sbl']

tango_base = "tango://antareshw.antares.frm2.tum.de:10000/antares/"

devices = dict(
    sbl_l = device('nicos.devices.tango.Motor',
        description = 'Beam Limiter Left Blade',
        tangodevice = tango_base + 'copley/m06',
        lowlevel = True,
        abslimits = (-250, 250),
    ),
    sbl_r = device('nicos.devices.tango.Motor',
        description = 'Beam Limiter Right Blade',
        tangodevice = tango_base + 'copley/m07',
        lowlevel = True,
        abslimits = (-250, 250),
    ),
    sbl_b = device('nicos.devices.tango.Motor',
        description = 'Beam Limiter Bottom Blade',
        tangodevice = tango_base + 'copley/m08',
        lowlevel = True,
        abslimits = (-250, 250),
    ),
    sbl_t = device('nicos.devices.tango.Motor',
        description = 'Beam Limiter Top Blade',
        tangodevice = tango_base + 'copley/m09',
        lowlevel = True,
        abslimits = (-250, 250),
    ),
    sbl = device('nicos.devices.generic.Slit',
        description = 'Small Beam Limiter',
        left = 'sbl_l',
        right = 'sbl_r',
        top = 'sbl_t',
        bottom = 'sbl_b',
        opmode = 'offcentered',
        coordinates = 'opposite',
        pollinterval = 5,
        maxage = 10,
    ),
)
