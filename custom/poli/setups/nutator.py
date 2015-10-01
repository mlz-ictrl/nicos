description = 'POLI nutator'

group = 'optional'
includes = []

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    co_nutator1 = device('devices.tango.Sensor',
                         lowlevel = True,
                         tangodevice = tango_base + 'nutator1/rotenc',
                         unit = 'deg',
                        ),
    mo_nutator1 = device('devices.tango.Motor',
                         lowlevel = True,
                         tangodevice = tango_base + 'nutator1/rotmot',
                         abslimits = (-360, 360),
                         unit = 'deg',
                         precision = 0.1,
                        ),
    co_nutator2 = device('devices.tango.Sensor',
                         lowlevel = True,
                         tangodevice = tango_base + 'nutator2/rotenc',
                         unit = 'deg',
                        ),
    mo_nutator2 = device('devices.tango.Motor',
                         lowlevel = True,
                         tangodevice = tango_base + 'nutator2/rotmot',
                         abslimits = (-360, 360),
                         unit = 'deg',
                         precision = 0.1,
                        ),
    nutator1    = device('devices.generic.Axis',
                         description = 'nutator1 axis',
                         motor = 'mo_nutator1',
                         coder = 'co_nutator1',
                         obs = [],
                         fmtstr = '%.2f',
                         precision = 0.1,
                        ),
    nutator2    = device('devices.generic.Axis',
                         description = 'nutator2 axis',
                         motor = 'mo_nutator2',
                         coder = 'co_nutator2',
                         obs = [],
                         fmtstr = '%.2f',
                         precision = 0.1,
                        ),
)
