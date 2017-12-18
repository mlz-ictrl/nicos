description = 'Julabo "bio oven"'
group = 'optional'

includes = ['alias_T']

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    T_julabo = device('nicos.devices.tango.TemperatureController',
        description = 'temperature regulation',
        tangodevice = tango_base + 'humidity/tempctrl',
        pollinterval = 0.7,
        maxage = 2,
        unit = 'degC',
    ),
)

alias_config = {
    'T': {'T_julabo': 200},
    'Ts': {'T_julabo': 100},
}
