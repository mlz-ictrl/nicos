description = 'virtual PGAA devices'
group = 'basic'

sysconfig = dict(
    instrument = 'pgaa',
)

excludes = ['tas', 'sans']

devices = dict(
    pgaa     = device('devices.instrument.Instrument',
                      instrument = 'PGAA-V'
                     ),

    x  = device('devices.generic.VirtualMotor',
                      abslimits = (0, 200),
                      speed = 0.5,
                      unit = 'mm',
                     ),

    y   = device('devices.generic.VirtualMotor',
                      abslimits = (0, 200),
                      speed = 1,
                      unit = 'mm',
                     ),

    z  = device('devices.generic.VirtualMotor',
                      abslimits = (0, 200),
                      speed = 0.5,
                      unit = 'mm',
                      initval = 1,
                     ),

    phi  = device('devices.generic.VirtualMotor',
                      abslimits = (0, 361),
                      speed = 0.5,
                      unit = 'deg',
                      initval = 1,
                     ),

#   det      = device('devices.generic.virtual.Virtual2DDetector',
#                     spotsize = 'det_pos',
#                     subdir = '2ddata',
#                    ),
)

startupcode = '''
SetMode('master')
# SetDetectors(det)
printinfo("============================================================")
printinfo("Welcome to the NICOS SANS demo setup.")
printinfo("Run count(1) to collect an image.")
printinfo("============================================================")
'''
