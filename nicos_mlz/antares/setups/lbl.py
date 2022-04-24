description = 'Large Beam Limiter in Experimental Chamber 2'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    lbl_l = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Left Blade',
        tangodevice = tango_base + 'fzjs7/Limit_l_left',
        visibility = (),
        abslimits = (-400, 400),
        userlimits = (-400, 400),
    ),
    lbl_r = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Right Blade',
        tangodevice = tango_base + 'fzjs7/Limit_l_right',
        visibility = (),
        abslimits = (-400, 400),
        userlimits = (-400, 400),
    ),
    lbl_b = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Bottom Blade',
        tangodevice = tango_base + 'fzjs7/Limit_l_bottom',
        visibility = (),
        abslimits = (-400, 400),
        userlimits = (-400, 400),
    ),
    lbl_t = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Top Blade',
        tangodevice = tango_base + 'fzjs7/Limit_l_top',
        visibility = (),
        abslimits = (-400, 400),
        userlimits = (-400, 400),
    ),
    lbl = device('nicos.devices.generic.Slit',
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

monitor_blocks = dict(
    default = Block('Large Beam Limiter',
        [
            BlockRow(
                Field(dev='lbl', name='lbl  [center[x,y], width[x,y]]', width=28),
            ),
        ],
        setups=setupname,
    ),
)
