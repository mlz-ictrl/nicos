description = 'test triple-axis setup'
group = 'basic'

modules = ['nicos.commands.tas']

includes = ['temperature']

sysconfig = dict(
    instrument = 'tas',
)

devices = dict(
    tas      = device('devices.tas.TAS',
                      description = 'test triple-axis spectrometer',
                      instrument = 'VTAS',
                      responsible = 'R. Esponsible <responsible@frm2.tum.de>',
                      energytransferunit = 'meV',
                      scanconstant = 1.5,
                      scanmode = 'CKF',
                      scatteringsense = (1, -1, 1),
                      axiscoupling = False,
                      collimation = '60 30 30 60',
                      cell = 'Sample',
                      phi = 'phi',
                      psi = 'psi',
                      mono = 'mono',
                      ana = 'ana',
                      alpha = None,
                     ),

    phi      = device('devices.generic.VirtualMotor',
                      abslimits = (-180, 180),
                      curvalue = -38.942,
                      unit = 'deg',
                     ),

    alpha    = device('devices.generic.VirtualMotor',
                      abslimits = (0, 50),
                      unit = 'deg',
                     ),

    psi      = device('devices.generic.VirtualMotor',
                      abslimits = (0, 360),
                      curvalue = 70.529,
                      unit = 'deg',
                     ),

    mono     = device('devices.tas.Monochromator',
                      unit = 'A-1',
                      dvalue = 3.355,
                      theta = 'mth',
                      twotheta = 'mtt',
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10),
                     ),

    mth      = device('devices.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (0, 90),
                      precision = 0.05,
                      curvalue = 38.628,
                     ),

    mtt      = device('devices.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (0, 180),
                      precision = 0.05,
                      curvalue = 77.256,
                     ),

    ana      = device('devices.tas.Monochromator',
                      unit = 'A-1',
                      dvalue = 3.355,
                      theta = 'ath',
                      twotheta = 'att',
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10),
                     ),

    ath      = device('devices.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-90, 90),
                      precision = 0.05,
                      curvalue = 38.628,
                     ),

    att      = device('devices.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      curvalue = 77.256,
                     ),

    ki       = device('devices.tas.Wavevector',
                      unit = 'A-1',
                      base = 'mono',
                      tas = 'tas',
                      scanmode = 'CKI',
                      abslimits = (0, 10),
                     ),

    kf       = device('devices.tas.Wavevector',
                      unit = 'A-1',
                      base = 'ana',
                      tas = 'tas',
                      scanmode = 'CKF',
                      abslimits = (0, 10),
                     ),

    Ei       = device('devices.tas.Energy',
                      unit = 'meV',
                      base = 'mono',
                      tas = 'tas',
                      scanmode = 'CKI',
                      abslimits = (0, 200)),

    Ef       = device('devices.tas.Energy',
                      unit = 'meV',
                      base = 'ana',
                      tas = 'tas',
                      scanmode = 'CKF',
                      abslimits = (0, 200)),

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
                      left = 'ssl',
                      right = 'ssr',
                      bottom = 'ssb',
                      top = 'sst',
                      opmode = 'offcentered',
                     ),

    vdet     = device('devices.tas.virtual.VirtualTasDetector',
                      tas = 'tas',
                      background = 1,
                     ),

    ec       = device('devices.tas.EulerianCradle',
                      cell = 'Sample',
                      tas = 'tas',
                      chi = 'echi',
                      omega = 'ephi'),
    echi     = device('devices.generic.VirtualMotor',
                      abslimits = (-180, 180),
                      curvalue = 0,
                      unit = 'deg',
                     ),
    ephi     = device('devices.generic.VirtualMotor',
                      abslimits = (-180, 180),
                      curvalue = 0,
                      unit = 'deg',
                     ),
)

startupcode = '''
SetDetectors(vdet)
AddEnvironment(T)
printinfo("============================================================")
printinfo("Welcome to the NICOS demo setups.")
printinfo("This demo is configured as a virtual triple-axis instrument.")
printinfo("Try doing an elastic scan over a Bragg peak, e.g.")
printinfo("  qcscan((1, 0, 0, 0), (0.002, 0, 0, 0), 10, t=1, kf=1.55)")
printinfo("or an energy scan, e.g.")
printinfo("  qscan((1, 0.2, 0, 4), (0, 0, 0, 0.2), 21, t=1, kf=2)")
printinfo("============================================================")
'''
