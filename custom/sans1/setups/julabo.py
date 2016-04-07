description = 'Julabo Presto temperature controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://julabo.sans1.frm2:10000/box/'

devices = dict(
    T_julabo = device('devices.tango.TemperatureController',
                       description = 'The regulated temperature',
                       tangodevice = tango_base + 'julabo/control',
                       abslimits = (-40, 250),
                       unit = 'C',
                       fmtstr = '%.2f',
                       precision = 0.1,
                      ),
)

alias_config = {
    'T':  {'T_julabo': 100},
    'Ts': {'T_julabo': 100},
}
