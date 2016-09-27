description = 'virtual triple-axis spectrometer'
group = 'basic'

modules = ['commands.tas']

excludes = []

includes = ['cryo', 'source']

sysconfig = dict(
    instrument = 'tas',
    datasinks = ['filesink'],
)

devices = dict(
    tas      = device('devices.tas.TAS',
                      description = 'virtual triple-axis spectrometer',
                      instrument = 'VTAS',
                      responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
                      website = 'http://www.nicos-controls.org',
                      operators = ['NICOS developer team', ],
                      facility = 'NICOS demo instruments',
                      energytransferunit = 'meV',
                      scatteringsense = (-1, 1, -1),
                      axiscoupling = False,
                      collimation = '60 30 30 60',
                      cell = 'Sample',
                      phi = 'phi',
                      psi = 'sth',
                      mono = 'mono',
                      ana = 'ana',
                      alpha = None,
                     ),

    phi      = device('devices.generic.VirtualMotor',
                      description = 'sample scattering angle',
                      abslimits = (-180, 180),
                      unit = 'deg',
                      speed = 1,
                     ),

    alpha    = device('devices.generic.VirtualMotor',
                      description = 'angle between ki and q',
                      abslimits = (0, 50),
                      unit = 'deg',
                     ),

    sth      = device('devices.generic.DeviceAlias',
                      alias = 'psi',
                     ),

    psi      = device('devices.generic.VirtualMotor',
                      description = 'sample rotation angle',
                      abslimits = (0, 360),
                      unit = 'deg',
                      speed = 2,
                     ),

    mono     = device('devices.tas.Monochromator',
                      description = 'monochromator wavevector',
                      unit = 'A-1',
                      dvalue = 3.355,
                      theta = 'mth',
                      twotheta = 'mtt',
                      focush = None,
                      focusv = None,
                      abslimits = (0.1, 10),
                      warnlimits = (1.0, 3.0),
                      crystalside = -1,
                     ),

    mth      = device('devices.generic.VirtualMotor',
                      description = 'monochromator rocking angle',
                      unit = 'deg',
                      abslimits = (-90, 0),
                      precision = 0.05,
                      speed = 0.5,
                     ),

    mtt      = device('devices.generic.VirtualMotor',
                      description = 'monochromator scattering angle',
                      unit = 'deg',
                      abslimits = (-180, 0),
                      precision = 0.05,
                      speed = 0.5,
                     ),

    ana      = device('devices.tas.Monochromator',
                      description = 'analyzer wavevector',
                      unit = 'A-1',
                      dvalue = 3.355,
                      theta = 'ath',
                      twotheta = 'att',
                      focush = None,
                      focusv = None,
                      abslimits = (0.1, 10),
                      crystalside = -1,
                     ),

    ath      = device('devices.generic.VirtualMotor',
                      description = 'analyzer rocking angle',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      speed = 0.5,
                     ),

    att      = device('devices.generic.VirtualMotor',
                      description = 'analyzer scattering angle',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      speed = 0.5,
                     ),

    ki       = device('devices.tas.Wavevector',
                      description = 'incoming wavevector',
                      unit = 'A-1',
                      base = 'mono',
                      tas = 'tas',
                      scanmode = 'CKI'
                     ),

    kf       = device('devices.tas.Wavevector',
                      description = 'outgoing wavevector',
                      unit = 'A-1',
                      base = 'ana',
                      tas = 'tas',
                      scanmode = 'CKF',
                     ),

    Ei       = device('devices.tas.Energy',
                      description = 'incoming energy',
                      unit = 'meV',
                      base = 'mono',
                      tas = 'tas',
                      scanmode = 'CKI',
                     ),

    Ef       = device('devices.tas.Energy',
                      description = 'outgoing energy',
                      unit = 'meV',
                      base = 'ana',
                      tas = 'tas',
                      scanmode = 'CKF',
                     ),

    ssl      = device('devices.generic.VirtualMotor',
                      abslimits = (-20, 40),
                      lowlevel = True,
                      unit = 'mm',
                     ),
    ssr      = device('devices.generic.VirtualMotor',
                      abslimits = (-40, 20),
                      lowlevel = True,
                      unit = 'mm',
                     ),
    ssb      = device('devices.generic.VirtualMotor',
                      abslimits = (-50, 30),
                      lowlevel = True,
                      unit = 'mm',
                     ),
    sst      = device('devices.generic.VirtualMotor',
                      abslimits = (-30, 50),
                      lowlevel = True,
                      unit = 'mm',
                     ),
    ss       = device('devices.generic.Slit',
                      description = 'sample slit',
                      left = 'ssl',
                      right = 'ssr',
                      bottom = 'ssb',
                      top = 'sst',
                      opmode = 'offcentered',
                     ),

    vdet     = device('devices.tas.virtual.VirtualTasDetector',
                      description = 'simulated TAS intensity',
                      tas = 'tas',
                      background = 1,
                      realtime = True,
                     ),

    ec       = device('devices.tas.EulerianCradle',
                      description = 'Eulerian cradle',
                      cell = 'Sample',
                      tas = 'tas',
                      chi = 'echi',
                      omega = 'ephi'),
    echi     = device('devices.generic.VirtualMotor',
                      description = 'big Euler circle',
                      abslimits = (-180, 180),
                      unit = 'deg',
                     ),
    ephi     = device('devices.generic.VirtualMotor',
                      description = 'small Euler circle',
                      abslimits = (-180, 180),
                      unit = 'deg',
                     ),

    TBeFilter   = device('devices.generic.VirtualTemperature',
                         description = 'Beryllium filter temperature',
                         abslimits = (0, 100),
                         warnlimits = (0, 70),
                         unit = 'K'),

    Shutter     = device('devices.generic.ManualSwitch',
                         description = 'Instrument shutter',
                         states = ['open', 'closed']),
)

alias_config = {
    'sth': {'psi': 0},
}

startupcode = '''
if mth() == 0:
    mth.speed = mtt.speed = ath.speed = att.speed = psi.speed = phi.speed = 0
    reset(tas)
    mono(1.55)
    kf(1.55)
    Sample.lattice = [3.5, 3.5, 3.5]
    tas(1,0,0,0)
    mth.speed = mtt.speed = 0.5
    psi.speed = 2
    phi.speed = 1
    ath.speed = att.speed = 0.5
SetDetectors(vdet)
AddEnvironment(T)
printinfo("============================================================")
printinfo("Welcome to the NICOS triple-axis demo setup.")
printinfo("This demo is configured as a virtual triple-axis instrument.")
printinfo("Try doing an elastic scan over a Bragg peak, e.g.")
printinfo("  > qcscan((1, 0, 0, 0), (0.002, 0, 0, 0), 10, t=1, kf=1.4)")
printinfo("or an energy scan, e.g.")
printinfo("  > qscan((1, 0.2, 0, 4), (0, 0, 0, 0.2), 21, t=1, kf=1.55)")
printinfo("============================================================")
'''
