description = 'Julabo bio furnace'
includes = ['system']

devices = dict(
    julabobus = device('nicos.toftof.julabo.HaakeRS232Driver',
                       tacodevice = '//toftofsrv/toftof/rs232/ifhubermot1',
                       maxtries = 5,
                       lowlevel = False),

    bio = device('nicos.toftof.julabo.Julabo',
                 bus = 'julabobus',
                 thermostat_type = 'JulaboF32HD',
                 userlimits = (-40, 160),
                 abslimits = (-50, 200),
                 rampType = 1,
                 rampRate = 0.1,
                 tolerance = 0.2,
                 unit = 'degC',
                 fmtstr = '%g'),
)

startupcode = """
Ts = bio
T = bio
"""
