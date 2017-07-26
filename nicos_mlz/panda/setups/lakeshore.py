description = 'LakeShore 340 cryo controller'

includes = ['alias_T']
group = 'optional'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    T_ls340   = device('nicos.devices.tango.TemperatureController',
                       description = 'PANDA lakeshore controller',
                       tangodevice = tango_base + 'ls340/control',
                       maxage = 2,
                       abslimits = (0, 300),
                      ),
    T_ls340_A = device('nicos.devices.tango.Sensor',
                       description = 'PANDA lakeshore Sensor A',
                       tangodevice = tango_base + 'ls340/sensora',
                       maxage = 2,
                      ),
    T_ls340_B = device('nicos.devices.tango.Sensor',
                       description = 'PANDA lakeshore Sensor B',
                       tangodevice = tango_base + 'ls340/sensorb',
                       maxage = 2,
                      ),
    T_ls340_C = device('nicos.devices.tango.Sensor',
                       description = 'PANDA lakeshore Sensor C',
                       tangodevice = tango_base + 'ls340/sensorc',
                       maxage = 2,
                      ),
    T_ls340_D = device('nicos.devices.tango.Sensor',
                       description = 'PANDA lakeshore Sensor D',
                       tangodevice = tango_base + 'ls340/sensord',
                       maxage = 2,
                      ),
    compressor_switch = device('nicos.devices.tango.NamedDigitalOutput',
                               description = 'PANDA cryo compressor switch',
                               tangodevice = tango_base + 'ls340/relay1',
                               mapping = {'off': 0, 'on': 1},
                              ),
)

alias_config = {
    'T': {'T_ls340': 200},
    'Ts': {'T_ls340_B': 100, 'T_ls340_A': 90, 'T_ls340_C': 80, 'T_ls340_D': 70},
}
