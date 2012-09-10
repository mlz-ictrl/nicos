description = 'FRM-II high temperature furnace'
includes = ['system']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    oven = device('nicos.taco.TemperatureController',
                  tacodevice = '//%s/toftof/htf/control' % (nethost, ),
                  userlimits = (0, 2000),
                  abslimits = (0, 2000),
                  rampRate = 0.1,
                  unit = 'C',
                  fmtstr = '%g'),
)

startupcode = """
Ts = oven
T = oven
SetEnvironment(Ts, T)
"""
