description = 'LakeShore 336 cryo controller'

includes = ['alias_T']
group = 'optional'

tango_base = 'tango://phys.panda.frm2:10000/panda/'

devices = dict(
    T_ls_hts = device('nicos.devices.tango.TemperatureController',
        description = 'PANDA lakeshore controller',
        tangodevice = tango_base + 'ls_hts/control',
        maxage = 6,
        abslimits = (0, 300),
    ),
    T_ls_hts_A = device('nicos.devices.tango.Sensor',
        description = 'Pt1000 Sensor A',
        tangodevice = tango_base + 'ls_hts/sensora',
        maxage = 6,
    ),
    T_ls_hts_D = device('nicos.devices.tango.Sensor',
        description = 'Thermoelement Sensor D',
        tangodevice = tango_base + 'ls_hts/sensord',
        maxage = 6,
    ),
    ls_hts_heaterpower = device('nicos.devices.tango.AnalogOutput',
        description = 'PANDA heater switch',
        tangodevice = tango_base + 'ls_hts/heater',
        maxage = 6,
    ),
)

alias_config = {
    'T': {'T_ls_hts': 200},
    'Ts': {'T_ls_hts_A': 85, 'T_ls_hts_D': 65},
}
