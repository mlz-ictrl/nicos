description = 'STRESS-SPEC setup with Tensile rigg Eulerian cradle'

group = 'basic'

includes = ['system', 'mux', 'monochromator', 'detector', 'sampletable',
            'primaryslit', 'slits', ]

excludes = ['eulerian_huber', 'eulerian_newport', 'robot']

sysconfig = dict(
    datasinks = ['caresssink'],
)

servername = 'VME'

nameservice = 'stressictrl'

devices = dict(
    chis = device('devices.vendor.caress.Motor',
                  description = 'Tensile CHIS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 3319.25,
                  abslimits = (20, 130),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'CHIS 115 11 0x00f1e000 3 350 2000 200 1 0 0 0 0 1 '
                           '5000 1 10 0 0 0'
                 ),
    phis = device('devices.vendor.caress.Motor',
                  description = 'Tensile PHIS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 2048,
                  abslimits = (-360, 360),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  # TODO: check which is the correct setup
                  config = 'PHIS 115 11 0x00f1d000 4 100 100 10 1 0 0 0 0 1 '
                           '5000 1 10 0 0 0',
                  # config = 'PHIS 115 11 0x00f1d000 4 30 20 2 1 0 0 0 0 1 '
                  #          '5000 1 10 0 0 0',
                 ),
)
