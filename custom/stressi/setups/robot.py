description = 'STRESS-SPEC setup with robot'

group = 'basic'

includes = ['system', 'mux', 'monochromator', 'detector',
            'primaryslit', 'slits', 'reactor']

excludes = []

sysconfig = dict(
    datasinks = ['caresssink'],
)

servername = 'VME'

nameservice = 'stressictrl'

devices = dict(
    chis = device('devices.vendor.caress.Motor',
                  description = 'HWB CHIS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 3319.25,
                  abslimits = (20, 130),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'CHIS 114 11 0x00f1e000 3 -4095 8000 800 2 24 50 1 '
                           '0 1 5000 1 10 0 0 0',
                 ),
    phis = device('devices.vendor.caress.Motor',
                  description = 'HWB PHIS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 2048,
                  abslimits = (-360, 360),
                  userlimits = (-200, 200),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'PHIS 114 11 0x00f1d000 4 2048 1200 102 2 24 50 1 0'
                           ' 1 5000 1 10 0 0 0',
                 ),
)
