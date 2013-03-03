description = 'virtual SANS devices'
group = 'basic'

devices = dict(
    tube     = device('devices.generic.VirtualMotor',
                      abslimits = (0, 100),
                      speed = 0.5,
                      unit = 'm',
                     ),

    guide_m  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 10),
                      speed = 0.5,
                      unit = 'mm',
                     ),
    guide    = device('devices.generic.Switcher',
                      moveable = 'guide_m',
                      states = ['guide', 'pol', 'nothing'],
                      values = [0, 5, 10],
                      precision = 0,
                     ),

    coll_m   = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 10),
                      speed = 0.02,
                      unit = 'mm',
                     ),
    coll     = device('devices.generic.Switcher',
                      moveable = 'coll_m',
                      states = ['20min', '40min', '60min'],
                      values = [0, 5, 10],
                      precision = 0,
                     ),
)
