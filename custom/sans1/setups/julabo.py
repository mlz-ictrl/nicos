description = 'Julabo Presto temperature controller'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://julabo.sans1.frm2:10000/box/'

devices = dict(
    T_julabo_intern = device('nicos.devices.tango.TemperatureController',
                       description = 'Julabo regulated to internal (bath) sensor',
                       tangodevice = tango_base + 'julabo/control',
                       abslimits = (-40, 250),
                       unit = 'C',
                       fmtstr = '%.2f',
                       precision = 0.1,
                      ),
    T_julabo_extern = device('nicos.devices.tango.TemperatureController',
                       description = 'Julabo regulated to external (sample) sensor',
                       tangodevice = tango_base + 'julabo/control_ext',
                       abslimits = (-40, 250),
                       unit = 'C',
                       fmtstr = '%.2f',
                       precision = 0.1,
                      ),
)

alias_config = {
    'T':  {'T_julabo_intern': 100, 'T_julabo_extern': 110},
    'Ts': {'T_julabo_intern': 100, 'T_julabo_extern': 110},
}
