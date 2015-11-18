description = 'Large Beam Limiter in Experimental Chamber 2'

group = 'optional'

tango_host = 'tango://slow.antares.frm2:10000'

devices = dict(
    lbl_l = device('devices.tango.Motor',
                   description = 'Beam Limiter Left Blade',
                   tangodevice = '%s/antares/fzjs7/Limit_l_left' % tango_host,
                   lowlevel = True,
                   abslimits = (-400, 400),
                   userlimits = (-400, 400),
                  ),
    lbl_r = device('devices.tango.Motor',
                   description = 'Beam Limiter Right Blade',
                   tangodevice = '%s/antares/fzjs7/Limit_l_right' % tango_host,
                   lowlevel = True,
                   abslimits = (-400, 400),
                   userlimits = (-400, 400),
                  ),
    lbl_b = device('devices.tango.Motor',
                   description = 'Beam Limiter Bottom Blade',
                   tangodevice = '%s/antares/fzjs7/Limit_l_bottom' % tango_host,
                   lowlevel = True,
                   abslimits = (-400, 400),
                   userlimits = (-400, 400),
                  ),
    lbl_t = device('devices.tango.Motor',
                   description = 'Beam Limiter Top Blade',
                   tangodevice = '%s/antares/fzjs7/Limit_l_top' % tango_host,
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

