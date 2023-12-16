description = 'Small Beam Limiter in Experimental Chamber 1'

group = 'optional'

tango_base = 'tango://phytron01.nectar.frm2.tum.de:10000/'

devices = dict(
    nbl_l = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Left Blade',
        tangodevice = tango_base + 'box/nbl_l/mot',
        visibility = (),
    ),
    nbl_r = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Right Blade',
        tangodevice = tango_base + 'box/nbl_r/mot',
        visibility = (),
    ),
    nbl_t = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Top Blade',
        tangodevice = tango_base + 'box/nbl_t/mot',
        visibility = (),
    ),
    nbl_b = device('nicos.devices.entangle.Motor',
        description = 'Beam Limiter Bottom Blade',
        tangodevice = tango_base + 'box/nbl_b/mot',
        visibility = (),
    ),
    nbl = device('nicos_mlz.nectar.devices.BeamLimiter',
        description = 'NECTAR Beam Limiter',
        left = 'nbl_l',
        right = 'nbl_r',
        top = 'nbl_t',
        bottom = 'nbl_b',
        opmode = 'centered',
        coordinates = 'opposite',
        pollinterval = 5,
        maxage = 10,
        parallel_ref = True,
    ),
)
