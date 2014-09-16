description = 'Sample manipulation stage using servostar controller'
group = 'optional'

includes = []

devices = dict(
    stx = device('antares.servostar.ServoStarMotor',
                            description = 'Sample Translation X',
                            tacodevice = 'nectar/mani/x',
                            pollinterval = 5,
                            maxage = 12,
                            userlimits = (0, 1010),
                            abslimits = (0, 1010),
                          ),
    sty = device('antares.servostar.ServoStarMotor',
                            description = 'Sample Translation Y',
                            tacodevice = 'nectar/mani/y',
                            pollinterval = 5,
                            maxage = 12,
                            userlimits = (0, 580),
                            abslimits = (0, 580),
                          ),
    sry = device('antares.servostar.ServoStarMotor',
                            description = 'Sample Rotation around Y',
                            tacodevice = 'nectar/mani/phi',
                            pollinterval = 5,
                            maxage = 12,
                            userlimits = (0, 360),
                            abslimits = (0, 360),
                          ),
)

startupcode = '''
'''
