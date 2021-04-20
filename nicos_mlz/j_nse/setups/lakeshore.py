description = 'LakeShore 336 temperature controller'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    T_ls336 = device('nicos.devices.entangle.TemperatureController',
        description = 'lakeshore controller',
        tangodevice = tango_base + 'ls336/control1',
        abslimits = (0, 300),
    ),
    T_ls336_A = device('nicos.devices.entangle.Sensor',
        description = 'lakeshore Sensor A',
        tangodevice = tango_base + 'ls336/sensora',
    ),
    T_ls336_B = device('nicos.devices.entangle.Sensor',
        description = 'lakeshore Sensor B',
        tangodevice = tango_base + 'ls336/sensorb',
    ),
    T_ls336_C = device('nicos.devices.entangle.Sensor',
        description = 'lakeshore Sensor C',
        tangodevice = tango_base + 'ls336/sensorc',
    ),
    T_ls336_D = device('nicos.devices.entangle.Sensor',
        description = 'lakeshore Sensor D',
        tangodevice = tango_base + 'ls336/sensord',
    ),
    ls336_heaterpower = device('nicos.devices.entangle.AnalogOutput',
        description = 'heater switch',
        tangodevice = tango_base + 'ls336/range1',
    ),
)

