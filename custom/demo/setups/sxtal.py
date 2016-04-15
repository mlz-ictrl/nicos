description = 'virtual triple-axis spectrometer'
group = 'basic'

modules = ['commands.sxtal']

excludes = ['sans', 'refsans','tas', 'table']

includes = ['cryo']

sysconfig = dict(
    instrument = 'sxtal',
    datasinks = ['scanfilesink', 'hklfilesink'],
)

devices = dict(

    sxtal      = device('devices.sxtal.instrument.SXTal',
                      description = 'virtual sxtal diffractometer',
                      instrument = 'VSXTAL',
                      responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
                      website = 'http://www.nicos-controls.org',
                      operators = ['NICOS developer team', ],
                      facility = 'NICOS demo instruments',
                      ttheta='ttheta',
                      omega='omega',
                      chi='chi',
                      phi='phi',
                      mono='mono',
                     ),
    Sample = device('devices.sxtal.sample.SXTalSample',
                    description='Single crystal sample',
                    ),
    scanfilesink   = device('devices.datasinks.AsciiScanfileSink',
                        lowlevel = True,
                        settypes=set(('subscan',)),
                       ),
    hklfilesink   = device('devices.datasinks.AsciiScanfileSink',
                        lowlevel = True,
                        settypes=set(('scan',)),
                        filenametemplate=['hkl_%(scancounter)s.hkl',],
                       ),
    ttheta   = device('devices.generic.VirtualMotor',
                      description = 'sample scattering angle',
                      abslimits = (-180, 180),
                      unit = 'deg',
                      speed = 1,
                     ),

    omega   = device('devices.generic.VirtualMotor',
                      description = 'euler omega angle',
                      abslimits = (-180, 180),
                      unit = 'deg',
                      speed = 1,
                     ),
    chi   = device('devices.generic.VirtualMotor',
                      description = 'euler chi angle',
                      abslimits = (-180, 180),
                      unit = 'deg',
                      speed = 1,
                     ),

    phi      = device('devices.generic.VirtualMotor',
                      description = 'sample rotation angle',
                      abslimits = (-180, 180),
                      unit = 'deg',
                      speed = 2,
                     ),

    mono     = device('devices.tas.Monochromator',
                      description = 'monochromator wavelength',
                      unit = 'A',
                      dvalue = 3.355,
                      theta = 'mth',
                      twotheta = 'mtt',
                      focush = None,
                      focusv = None,
                      abslimits = (0.1, 10),
                      warnlimits = (1.0, 3.0),
                      scatteringsense = -1,
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

    vdetsxtal     = device('devices.sxtal.virtual.VirtualSXtalDetector',
                      description = 'simulated TAS intensity',
                      sxtal = 'sxtal',
                      background = 1,
                      realtime = True,
                     ),
    intensity     = device('devices.generic.detector.DummyDetector',
                           description = 'dummy for hkl scan',
                           lowlevel=True,
                           unit='cts'),

    Shutter     = device('devices.generic.ManualSwitch',
                         description = 'Instrument shutter',
                         states = ['open', 'closed']),
)

startupcode = '''
if mth() == 0:
    mth.speed = mtt.speed = ath.speed = att.speed = psi.speed = phi.speed = 0
    mono(0.7)
SetDetectors(vdetsxtal)
AddEnvironment(T)
printinfo("============================================================")
printinfo("Welcome to the NICOS singe xtal demo setup.")
printinfo("This demo is configured as a virtual single crystal instrument.")
printinfo("============================================================")
'''
