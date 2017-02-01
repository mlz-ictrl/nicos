description = 'Peltier temperature controller TLC40'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    T_peltier = device('devices.tango.TemperatureController',
                       description = 'The regulated temperature',
                       tangodevice = tango_base + 'tlc40/control',
                       abslimits = (5, 140),
                       unit = 'degC',
                       fmtstr = '%.2f',
                       precision = 0.1,
                       timeout = 1800.0,
                      ),
)

alias_config = {
    'T':  {'T_peltier': 110},  # higher than Julabo alone
    'Ts': {'T_peltier': 110},
}
