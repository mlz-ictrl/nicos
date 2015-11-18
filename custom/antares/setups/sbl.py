description = 'Small Beam Limiter in Experimental Chamber 1'

group = 'optional'

tango_host = 'tango://slow.antares.frm2:10000'

devices = dict(
    sbl_l = device('devices.tango.Motor',
                   description = 'Beam Limiter Left Blade',
                   tangodevice = '%s/antares/fzjs7/Limit_s_left' % tango_host,
                   lowlevel = True,
                   abslimits = (-250, 250),
                   userlimits = (-250, 250),
                  ),
    sbl_r = device('devices.tango.Motor',
                   description = 'Beam Limiter Right Blade',
                   tangodevice = '%s/antares/fzjs7/Limit_s_right' % tango_host,
                   lowlevel = True,
                   abslimits = (-250, 250),
                   userlimits = (-250, 250),
                  ),
    sbl_b = device('devices.tango.Motor',
                   description = 'Beam Limiter Bottom Blade',
                   tangodevice = '%s/antares/fzjs7/Limit_s_bottom' % tango_host,
                   lowlevel = True,
                   abslimits = (-250, 250),
                   userlimits = (-250, 250),
                  ),
    sbl_t = device('devices.tango.Motor',
                   description = 'Beam Limiter Top Blade',
                   tangodevice = '%s/antares/fzjs7/Limit_s_top' % tango_host,
                   lowlevel = True,
                   abslimits = (-250, 250),
                   userlimits = (-250, 250),
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
