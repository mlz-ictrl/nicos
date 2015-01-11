description = 'Julabo bio furnace'

group = 'optional'

includes = ['alias_T']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    bio = device('toftof.julabo.Controller',
                 description = 'Julabo temperature controller',
                 tacodevice = '//%s/toftof/rs232/ifbiofurnace' % (nethost,),
                 intern_extern = 0,
                 userlimits = (-40, 160),
                 abslimits = (-50, 200),
                 unit = 'degC',
                 fmtstr = '%g',
                ),
)

startupcode = """
Ts.alias = bio
T.alias = bio
SetEnvironment(Ts, T)
"""
