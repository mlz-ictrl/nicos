description = 'Lauda temperature controller with external sensor'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://localhost:10000/galaxi/'

devices = dict(
    T_lauda_intern = device('nicos.devices.tango.TemperatureController',
        description = 'Lauda regulated to internal (bath) sensor',
        tangodevice = tango_base + 'lauda/controller_int',
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        window = 10,
    ),
    T_lauda_extern = device('nicos.devices.tango.TemperatureController',
        description = 'Lauda regulated to external sensor',
        tangodevice = tango_base + 'lauda/controller_ext',
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        window = 10,
    ),
)

alias_config = {
    'T':  {'T_lauda_intern': 100, 'T_lauda_extern': 110},
    'Ts': {'T_lauda_intern': 100, 'T_lauda_extern': 110},
}
