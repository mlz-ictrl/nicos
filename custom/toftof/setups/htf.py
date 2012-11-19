description = 'FRM-II high temperature furnace'
includes = ['system']

includes = ['alias_T']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    oven = device('devices.taco.TemperatureController',
                  tacodevice = '//%s/toftof/htf/control' % (nethost, ),
                  userlimits = (0, 2000),
                  abslimits = (0, 2000),
                  rampRate = 0.1,
                  unit = 'C',
                  fmtstr = '%g'),
)

startupcode = """
Ts.alias = oven
T.alias = oven
AddEnvironment(Ts, T)
"""
