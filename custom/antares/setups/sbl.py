description = 'Small Beam Limiter in Experimental Chamber 1'

group = 'optional'

tango_base = 'tango://slow.antares.frm2:10000/antares/'

devices = dict(
    sbl_l = device('devices.tango.Motor',
                   description = 'Beam Limiter Left Blade',
                   tangodevice = tango_base + 'fzjs7/Limit_s_right',
                   lowlevel = True,
                   abslimits = (-250, 250),
                   userlimits = (-250, 250),
                  ),
    sbl_r = device('devices.tango.Motor',
                   description = 'Beam Limiter Right Blade',
                   tangodevice = tango_base + 'fzjs7/Limit_s_left',
                   lowlevel = True,
                   abslimits = (-250, 250),
                   userlimits = (-250, 250),
                  ),
    sbl_b = device('devices.tango.Motor',
                   description = 'Beam Limiter Bottom Blade',
                   tangodevice = tango_base + 'fzjs7/Limit_s_bottom',
                   lowlevel = True,
                   abslimits = (-250, 250),
                   userlimits = (-250, 250),
                  ),
    sbl_t = device('devices.tango.Motor',
                   description = 'Beam Limiter Top Blade',
                   tangodevice = tango_base + 'fzjs7/Limit_s_top',
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
