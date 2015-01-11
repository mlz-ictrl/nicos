description = 'Impac IGAR 12-LO pyrometer'

group = 'optional'

includes = ['alias_T']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    pyro = device('toftof.impac.TemperatureSensor',
                  description = 'Impac pyrometer thermometer',
                  tacodevice = '//%s/toftof/rs232/ifpyrometer' % (nethost, ),
                  unit = 'C',
                  fmtstr = '%.3f',
                 ),
)

startupcode = """
T.alias = pyro
Ts.alias = pyro
SetEnvironment(T, Ts)
"""
