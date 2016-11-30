description = 'POLI lifting counter'

group = 'lowlevel'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    co_lftctr = device('devices.tango.Sensor',
                      lowlevel = True,
                      tangodevice = tango_base + 'lftctr/lftctrenc',
                      unit = 'deg',
                     ),
    mo_lftctr = device('devices.tango.Motor',
                      lowlevel = True,
                      tangodevice = tango_base + 'lftctr/lftctrmot',
                      unit = 'deg',
                      precision = 0.01,
                     ),
    liftingctr = device('devices.generic.Axis',
                      description = 'lifting counter axis',
                      motor = 'mo_lftctr',
                      coder = 'co_lftctr',
                      pollinterval = 15,
                      maxage = 61,
                      fmtstr = '%.2f',
                      abslimits = (-4.2, 25),
                      precision = 0.01,
                     ),
#    liftingctr = device('devices.generic.VirtualMotor',
#                      description = 'lifting counter axis',
#                      pollinterval = 15,
#                      maxage = 61,
#                      fmtstr = '%.2f',
#                      abslimits = (-5, 30),
#                      precision = 0.01,
#                      unit = 'deg',
#                     ),

    lubrication = device('poli.lubrication.LubeSwitch',
                      description = 'lubrication switch',
                      tangodevice = tango_base + 'fzjdp_digital/lubrication',
                      lowlevel = True,
                     ),
)
