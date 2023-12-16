description = 'Small Beam Limiter in Experimental Chamber 1'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    sbl_l = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Left Blade',
        tangodevice = tango_base + 'fzjs7/Limit_s_left',
        visibility = (),
        abslimits = (-250, 250),
        userlimits = (-250, 250),
    ),
    sbl_r = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Right Blade',
        tangodevice = tango_base + 'fzjs7/Limit_s_right',
        visibility = (),
        abslimits = (-250, 250),
        userlimits = (-250, 250),
    ),
    sbl_b = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Bottom Blade',
        tangodevice = tango_base + 'fzjs7/Limit_s_bottom',
        visibility = (),
        abslimits = (-250, 250),
        userlimits = (-250, 250),
    ),
    sbl_t = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Top Blade',
        tangodevice = tango_base + 'fzjs7/Limit_s_top',
        visibility = (),
        abslimits = (-250, 250),
        userlimits = (-250, 250),
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

monitor_blocks = dict(
    default = Block('Small Beam Limiter',
        [
            BlockRow(
                Field(dev='sbl', name='sbl  [center[x,y], width[x,y]]', width=28),
            ),
        ],
        setups=setupname,
    ),
)
