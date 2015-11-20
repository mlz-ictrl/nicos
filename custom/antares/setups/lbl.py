description = 'Large Beam Limiter in Experimental Chamber 2'

group = 'optional'

tango_base = 'tango://slow.antares.frm2:10000/antares/'

devices = dict(
    lbl_l = device('devices.tango.Motor',
                   description = 'Beam Limiter Left Blade',
                   tangodevice = tango_base + 'fzjs7/Limit_l_left',
                   lowlevel = True,
                   abslimits = (-400, 400),
                   userlimits = (-400, 400),
                  ),
    lbl_r = device('devices.tango.Motor',
                   description = 'Beam Limiter Right Blade',
                   tangodevice = tango_base + 'fzjs7/Limit_l_right',
                   lowlevel = True,
                   abslimits = (-400, 400),
                   userlimits = (-400, 400),
                  ),
    lbl_b = device('devices.tango.Motor',
                   description = 'Beam Limiter Bottom Blade',
                   tangodevice = tango_base + 'fzjs7/Limit_l_bottom',
                   lowlevel = True,
                   abslimits = (-400, 400),
                   userlimits = (-400, 400),
                  ),
    lbl_t = device('devices.tango.Motor',
                   description = 'Beam Limiter Top Blade',
                   tangodevice = tango_base + 'fzjs7/Limit_l_top',
                   lowlevel = True,
                   abslimits = (-400, 400),
                   userlimits = (-400, 400),
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
