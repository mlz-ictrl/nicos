description = 'Laser distance measurement device on Amor'

group = 'lowlevel'

devices = dict(
    dimetix = device('nicos_sinq.amor.devices.dimetix.EpicsDimetix',
                     description = 'Laser distance measurement device',
                     readpv = 'SQ:AMOR:DIMETIX:DIST',
                     offset = -238,
                     visibility = ()
                     ),
    xlz = device('nicos_sinq.devices.epics.motor.SinqMotor',
                 description = 'Counter z position distance laser motor',
                 motorpv = 'SQ:AMOR:mota:xlz',
                 visibility = (),
                 ),
    laser_positioner = device('nicos.devices.generic.Switcher',
                              description = 'Position laser to read components',
                              moveable = 'xlz',
                              mapping = {
                                  'deflector': -0.1,
                                  'aux': -88.0,
                                  'slit2': -73.0,
                                  'sample': -52.0,
                                  'slit3': -63.0,
                                  'detector': -34.0,
                                  },
                              fallback = '<undefined>',
                              precision = 0,
                              visibility = ()
                              ),
    )
