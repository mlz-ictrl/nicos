description = 'Small Beam Limiter in Experimental Chamber 1'

group = 'optional'

tango_host = 'tango://cpci01.antares.frm2:10000'


devices = dict(
    sbl_l = device('devices.taco.Motor',
                   description = 'Beam Limiter Left Blade',
                   tacodevice = 'antares/copley/m06',
                   lowlevel = True,
                   abslimits = (-250, 250),
                  ),
    sbl_r = device('devices.taco.Motor',
                   description = 'Beam Limiter Right Blade',
                   tacodevice = 'antares/copley/m07',
                   lowlevel = True,
                   abslimits = (-250, 250),
                  ),
    sbl_b = device('devices.taco.Motor',
                   description = 'Beam Limiter Bottom Blade',
                   tacodevice = 'antares/copley/m08',
                   lowlevel = True,
                   abslimits = (-250, 250),
                  ),
    sbl_t = device('devices.taco.Motor',
                   description = 'Beam Limiter Top Blade',
                   tacodevice = 'antares/copley/m09',
                   lowlevel = True,
                   abslimits = (-250, 250),
                  ),

    sbl = device('devices.generic.Slit',
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
