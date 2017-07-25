description = 'LASCON pyrometer devices'

includes = ['alias_T']

excludes = []

group = 'optional'

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    Ts_lascon = device('nicos_mlz.toftof.devices.lascon.TemperatureSensor',
                       description = 'Sample temperature',
                       tacodevice = '//%s/toftof/pyro/network' % (nethost, ),
                       fmtstr = '%.3f',
                       unit = 'C',
                      ),
#   T_lascon = device('nicos_mlz.toftof.devices.lascon.TemperatureController',
#                     description = 'Sample temperature control',
#                     tacodevice = '//%s/toftof/pyro/network' % (nethost, ),
#                     fmtstr = '%.3f',
#                     unit = 'C',
#                     precision = 0.1,
#                     abslimits = [0, 1000],
#                    ),
)

alias_config = {
    'T': {'Ts_lascon': 200},
    'Ts': {'Ts_lascon': 100},
}
