description = 'Large sample manipulation stage using servostar controller'
group = 'optional'

includes = ['alias_sample']

devices = dict(
    stx_servostar = device('antares.servostar.ServoStarMotor',
                           description = 'Sample Translation X',
                           tacodevice = 'antares/mani/x',
                           pollinterval = 5,
                           maxage = 12,
                           userlimits = (0, 1010),
                           abslimits = (0, 1010),
                          ),
    sty_servostar = device('antares.servostar.ServoStarMotor',
                           description = 'Sample Translation Y',
                           tacodevice = 'antares/mani/y',
                           pollinterval = 5,
                           maxage = 12,
                           userlimits = (0, 580),
                           abslimits = (0, 580),
                          ),
    sry_servostar = device('antares.servostar.ServoStarMotor',
                           description = 'Sample Rotation around Y',
                           tacodevice = 'antares/mani/phi',
                           pollinterval = 5,
                           maxage = 12,
                          ),
)

startupcode = '''
stx.alias = 'stx_servostar'
sty.alias = 'sty_servostar'
sry.alias = 'sry_servostar'
'''
