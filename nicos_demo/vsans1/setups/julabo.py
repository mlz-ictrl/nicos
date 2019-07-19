description = 'Julabo Presto temperature controller'

group = 'optional'

includes = ['alias_T']

devices = dict(
    T_julabo_intern = device('nicos.devices.generic.VirtualRealTemperature',
        description = 'Julabo regulated to internal (bath) sensor',
        abslimits = (-40, 250),
        unit = 'C',
        fmtstr = '%.2f',
        precision = 0.1,
    ),
    T_julabo_extern = device('nicos.devices.generic.VirtualRealTemperature',
        description = 'Julabo regulated to external (sample) sensor',
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
