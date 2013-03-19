description = 'Julabo bio furnace'

group = 'optional'

includes = ['system']

nethost = 'toftofsrv'

devices = dict(
    bio = device('toftof.julabo.Julabo',
                 tacodevice = '//%s/toftof/rs232/ifbiofurnace' % (nethost,),
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
