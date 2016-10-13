description = 'STRESS-SPEC setup with Huber Eulerian cradle'

group = 'basic'

includes = ['system', 'mux', 'monochromator', 'detector', 'sampletable',
            'primaryslit', 'slits', 'reactor']

excludes = ['eulerian_newport', 'eulerian_tensile', 'robot']

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
                  coderoffset = -1114.738,
                  abslimits = (-5, 100),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'CHIS 114 11 0x00f1e000 3 -4095 8000 800 2 24 50 1 '
                           '0 1 5000 1 10 0 0 0',
                 ),
    phis = device('devices.vendor.caress.Motor',
                  description = 'HWB PHIS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 7380.467,
                  abslimits = (-720, 720),
                  userlimits = (-700, 700),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  # TODO Check the right settings
                  config = 'PHIS 114 11 0x00f1c000 2 2048 2040 204 2 24 50 1 0'
                           ' 1 5000 1 10 0 0 0',
                  # config = 'PHIS 114 11 0x00f1d000 4 2048 510 51 2 24 50 1 0'
                  #          ' 1 5000 1 10 0 0 0',
                  # config = 'PHIS 115 11 0x00f1d000 4 50 20 2 1 0 0 0 0 '
                  #          '1 5000 1 10 0 0 0',
                 ),
)
