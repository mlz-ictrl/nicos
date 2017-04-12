description = 'Julabo temperature controller'

group = 'optional'

includes = ['alias_T']
excludes = ['julabo22']

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'

devices = dict(
    T_julabo = device('kws1.julabo.TemperatureController',
                       description = 'The regulated temperature',
                       tangodevice = tango_base + 'julabo21/control',
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
