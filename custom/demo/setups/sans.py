description = 'virtual SANS devices'
group = 'basic'

sysconfig = dict(
    instrument = 'sans',
)

excludes = ['tas']
includes = ['cryo']

devices = dict(
    sans     = device('devices.instrument.Instrument',
                      instrument = 'SANS-V'
                     ),

    guide_m1  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 10),
                      speed = 0.5,
                      unit = 'mm',
                     ),
    guide1    = device('devices.generic.Switcher',
                      lowlevel = True,
                      moveable = 'guide_m1',
                      states = ['off', 'ng', 'P3', 'P4'],
                      values = [0, 3, 6, 9],
                      precision = 0,
                      blockingmove = False,
                     ),
    guide_m2  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 10),
                      speed = 0.5,
                      unit = 'mm',
                     ),
    guide2    = device('devices.generic.Switcher',
                      lowlevel = True,
                      moveable = 'guide_m2',
                      states = ['off', 'ng', 'P3', 'P4'],
                      values = [0, 3, 6, 9],
                      precision = 0,
                      blockingmove = False,
                     ),
    guide_m3  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 10),
                      speed = 0.5,
                      unit = 'mm',
                     ),
    guide3    = device('devices.generic.Switcher',
                      lowlevel = True,
                      moveable = 'guide_m3',
                      states = ['off', 'ng', 'P3', 'P4'],
                      values = [0, 3, 6, 9],
                      precision = 0,
                      blockingmove = False,
                     ),
    guide_m4  = device('devices.generic.VirtualMotor',
                      lowlevel = True,
                      abslimits = (0, 10),
                      speed = 0.5,
                      unit = 'mm',
                     ),
    guide4    = device('devices.generic.Switcher',
                      lowlevel = True,
                      moveable = 'guide_m4',
                      states = ['off', 'ng', 'P3', 'P4'],
                      values = [0, 3, 6, 9],
                      precision = 0,
                      blockingmove = False,
                     ),
    guide    = device('sans1.sans1switcher.MultiSwitcher',
                      moveable = ['guide1', 'guide2', 'guide3', 'guide4'],
                      states = ['off', '1m', '2m', '4m', '6m', 'P3', 'P4'],
                      values = [ ['off', 'off', 'off', 'off'],  # off
                                 ['off', 'off', 'off', 'ng' ],  # 1m
                                 ['off', 'off', 'ng',  'ng' ],  # 2m
                                 ['off', 'ng',  'ng',  'ng' ],  # 4m
                                 ['ng',  'ng',  'ng',  'ng' ],  # 6m
                                 ['P3',  'P3',  'P3',  'P3' ],  # P3
                                 ['P4',  'P4',  'P4',  'P4' ],  # P4
                                ],
                      precision = 0,
                     ),

    #~ coll_m   = device('devices.generic.VirtualMotor',
                      #~ lowlevel = True,
                      #~ abslimits = (0, 10),
                      #~ speed = 1,
                      #~ unit = 'deg',
                     #~ ),
    #~ coll     = device('devices.generic.Switcher',
                      #~ description = 'collimation',
                      #~ moveable = 'coll_m',
                      #~ states = ['off','2m','P3','P4'],
                      #~ values = [0, 2, 4, 8],
                      #~ precision = 0,
                     #~ ),

    det_pos1  = device('devices.generic.VirtualMotor',
                      description = 'detector1 position in the tube',
                      abslimits = (0, 21),
                      speed = 0.5,
                      unit = 'm',
                      initval = 1,
                     ),

    det_pos1_x  = device('devices.generic.VirtualMotor',
                      description = 'horizontal offset of detector inside tube',
                      abslimits = (-1, 5),
                      speed = 0.5,
                      unit = 'm',
                      initval = 0,
                     ),

    det_pos1_tilt  = device('devices.generic.VirtualMotor',
                      description = 'tilt of detector',
                      abslimits = (-40, 40),
                      speed = 0.5,
                      unit = 'deg',
                      initval = 0,
                     ),

    det_pos2  = device('devices.generic.VirtualMotor',
                      description = 'detector2 position in the tube',
                      abslimits = (1, 22),
                      speed = 0.5,
                      unit = 'm',
                      initval = 10,
                     ),

    det      = device('devices.generic.virtual.Virtual2DDetector',
                      distance = 'det_pos1',
                      collimation = 'guide',
                      subdir = '2ddata',
                     ),

    det_HV   = device('devices.generic.VirtualMotor',
                      description = 'high voltage at the detector',
                      requires = {'level': 'admin'},
                      abslimits = (0, 1000),
                      unit = 'V',
                      initval = 1000,
                      speed = 10,
                     ),
)

startupcode = '''
SetMode('master')
SetDetectors(det)
printinfo("============================================================")
printinfo("Welcome to the NICOS SANS demo setup.")
printinfo("Run count(1) to collect an image.")
printinfo("============================================================")
'''
