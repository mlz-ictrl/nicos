description = 'high temperature furnace'
includes = ['system']

devices = dict(
    oven = device('nicos.taco.temperature.Controller',
		 userlimits = (0, 2000),
                 abslimits = (0, 2000),
                 rampRate = 0.1,
                 unit = 'K',
                 fmtstr = '%g'),
)

startupcode = """
Ts = oven
T = oven
"""
