description = 'LASCON pyrometer devices'

includes = ['alias_T']

group = 'optional'

tango_base = 'tango://tofhw.toftof.frm2.tum.de:10000/toftof/pyro/'

devices = dict(
    Ts_lascon = device('nicos_mlz.toftof.devices.lascon.TemperatureSensor',
        description = 'Sample temperature',
        tangodevice = tango_base + 'network',
        fmtstr = '%.3f',
        unit = 'C',
    ),
    #   T_lascon = device('nicos_mlz.toftof.devices.lascon.TemperatureController',
    #       description = 'Sample temperature control',
    #       tangodevice = tango_base + 'network',
    #       fmtstr = '%.3f',
    #       unit = 'C',
    #       precision = 0.1,
    #       abslimits = [0, 1000],
    #   ),
)

alias_config = {
    'T': {'Ts_lascon': 200},
    'Ts': {'Ts_lascon': 100},
}
