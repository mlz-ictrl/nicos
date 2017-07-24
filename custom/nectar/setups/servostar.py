description = 'Sample manipulation stage using servostar controller'
group = 'optional'

includes = []

nethost = 'nectarsrv.nectar.frm2'

devices = dict(
    stx = device('nicos_mlz.antares.devices.servostar.ServoStarMotor',
                 description = 'Sample Translation X',
                 tacodevice = '//%s/nectar/mani/x' % nethost,
                 pollinterval = 5,
                 maxage = 12,
                 userlimits = (0, 1010),
                 abslimits = (0, 1010),
                 comtries = 5,
                ),
    sty = device('nicos_mlz.antares.devices.servostar.ServoStarMotor',
                 description = 'Sample Translation Y',
                 tacodevice = '//%s/nectar/mani/y' % nethost,
                 pollinterval = 5,
                 maxage = 12,
                 userlimits = (0, 580),
                 abslimits = (0, 580),
                 comtries = 5,
                ),
    sry = device('nicos_mlz.antares.devices.servostar.ServoStarMotor',
                 description = 'Sample Rotation around Y',
                 tacodevice = '//%s/nectar/mani/phi' % nethost,
                 pollinterval = 5,
                 maxage = 12,
                 userlimits = (0, 360),
                 abslimits = (0, 360),
                 comtries = 5,
                ),
)
