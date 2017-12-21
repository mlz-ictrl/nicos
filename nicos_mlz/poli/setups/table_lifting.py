description = 'POLI lifting counter'

group = 'lowlevel'
excludes = ['table_lifting_virtual']

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    co_lftctr = device('nicos.devices.tango.Sensor',
        lowlevel = True,
        tangodevice = tango_base + 'lftctr/lftctrenc',
        unit = 'deg',
    ),
    mo_lftctr = device('nicos.devices.tango.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'lftctr/lftctrmot',
        unit = 'deg',
        precision = 0.01,
    ),
    liftingctr = device('nicos.devices.generic.Axis',
        description = 'lifting counter axis',
        motor = 'mo_lftctr',
        coder = 'co_lftctr',
        pollinterval = 15,
        maxage = 61,
        fmtstr = '%.2f',
        abslimits = (-4.2, 30),
        precision = 0.01,
    ),
    lubrication = device('nicos_mlz.poli.devices.lubrication.LubeSwitch',
        description = 'lubrication switch',
        tangodevice = tango_base + 'fzjdp_digital/lubrication',
        lowlevel = True,
    ),
)
