description = 'Julabo bio furnace'
includes = ['system']

devices = dict(
    julabobus = device('nicos.toftof.julabo.HaakeRS232Driver',
                 tacodevice = '//toftofsrv/toftof/rs232/ifbiofurnace',
                 maxtries = 5,
                 lowlevel = False),

    bio = device('nicos.toftof.julabo.Julabo',
                 bus = 'julabobus',
		 intern_extern = 0,
                 userlimits = (-40, 160),
                 abslimits = (-50, 200),
                 unit = 'degC',
                 fmtstr = '%g'),
)

startupcode = """
Ts = bio
T = bio
SetEnvironment(Ts, T)
"""
