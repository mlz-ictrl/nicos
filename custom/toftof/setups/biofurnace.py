description = 'Julabo bio furnace'

group = 'optional'

includes = ['system']

devices = dict(
    bio = device('toftof.julabo.Julabo',
                 tacodevice = '//toftofsrv/toftof/rs232/ifbiofurnace',
                 intern_extern = 0,
                 userlimits = (-40, 160),
                 abslimits = (-50, 200),
                 unit = 'degC',
                 fmtstr = '%g',
                ),
)

startupcode = """
Ts = bio
T = bio
SetEnvironment(Ts, T)
"""
