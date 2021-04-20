description = 'Peltier controller for rotating sample environment'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    T_rotpeltier = device('nicos.devices.entangle.TemperatureController',
        description = 'The regulated temperature',
        tangodevice = tango_base + 'rotpeltier/ctrl',
        unit = 'degC',
        fmtstr = '%.1f',
        precision = 0.5,
        timeout = 45 * 60.,
    ),
)

alias_config = {
    'T':  {'T_rotpeltier': 100},
    'Ts': {'T_rotpeltier': 100},
}
