description = 'Large Beam Limiter in Experimeantal Chamber 2'

group = 'optional'

devices = dict(
    lbl_l = device('devices.taco.Motor',
                    description = 'Beam Limiter Left Blade',
                    tacodevice = 'antares/copley/m10',
                    lowlevel = True,
                    abslimits = (0, 400),
                  ),
    lbl_r = device('devices.taco.Motor',
                    description = 'Beam Limiter Right Blade',
                    tacodevice = 'antares/copley/m11',
                    lowlevel = True,
                    abslimits = (0, 400),
                  ),
    lbl_b = device('devices.taco.Motor',
                    description = 'Beam Limiter Bottom Blade',
                    tacodevice = 'antares/copley/m12',
                    lowlevel = True,
                    abslimits = (0, 400),
                  ),
    lbl_t = device('devices.taco.Motor',
                    description = 'Beam Limiter Top Blade',
                    tacodevice = 'antares/copley/m13',
                    lowlevel = True,
                    abslimits = (0, 400),
                  ),

    lbl = device('devices.generic.Slit',
                  description = 'Large Beam Limiter',
                  left = 'lbl_l',
                  right = 'lbl_r',
                  top = 'lbl_t',
                  bottom = 'lbl_b',
                  opmode = 'offcentered',
                  coordinates = 'opposite',
                  pollinterval = 5,
                  maxage = 10,
                ),
)

