description = 'LASCON pyrometer devices'

includes = ['alias_T']

excludes = []

group = 'optional'

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    Ts_lascon = device('toftof.lascon.TemperatureSensor',
                       description = 'Sample temperature',
                       tacodevice = '//%s/toftof/pyro/network' % (nethost, ),
                       fmtstr = '%.3f',
                       unit = 'C',
                      ),
#   T_lascon = device('toftof.lascon.TemperatureController',
#                     description = 'Sample temperature control',
#                     tacodevice = '//%s/toftof/pyro/network' % (nethost, ),
#                     fmtstr = '%.3f',
#                     unit = 'C',
#                     precision = 0.1,
#                     abslimits = [0, 1000],
#                    ),
)

startupcode = """
T.alias = Ts_lascon
Ts.alias = Ts_lascon
SetEnvironment(T, Ts)
"""
