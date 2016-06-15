description = 'Water-Julabo temperature controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    T_julabo = device('devices.tango.TemperatureController',
                       description = 'The regulated temperature',
                       tangodevice = tango_base + 'waterjulabo/control',
                       abslimits = (10, 80),
                       unit = 'degC',
                       fmtstr = '%.2f',
                       precision = 0.1,
                       timeout = 45*60.,
                      ),
)

alias_config = {
    'T':  {'T_julabo': 100},
    'Ts': {'T_julabo': 100},
}
