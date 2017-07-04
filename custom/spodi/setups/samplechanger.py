description = 'CARESS HWB Devices'

group = 'optional'

servername = 'VMESPODI'

nameservice = 'spodisrv.spodi.frm2'

includes = []

devices = dict(
    samsm = device('nicos.devices.vendor.caress.Motor',
                   description = 'HWB SAMS',
                   fmtstr = '%.2f',
                   unit = 'deg',
                   coderoffset = -9807.33,
                   abslimits = (-360, 370),
                   nameserver = '%s' % (nameservice,),
                   objname = '%s' % (servername),
                   config = 'SAMS 114 11 0x00f1d000 1 409 2000 100 2 24 50 '
                            '-1 0 1 4000 1 10 10 0 0',
                   lowlevel = True,
                  ),
    # Sample changer ***Attention SAMR is also CHIT (Load Frame Chi)***
    samr = device('nicos.devices.vendor.caress.Motor',
                  description = 'HWB SAMR',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 0,
                  abslimits = (-360, 360),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'SAMR 115 11 0x00f1e000 4 644 10000 1000 1 0 50 '
                           '1 0 1 4000 1 10 10 0 0',
                 ),
    sams = device('nicos.devices.generic.Switcher',
                  description = 'Sample Changer drum',
                  moveable = 'samsm',
                  mapping = {'S1': 1.50,
                             'S2': 19.56,
                             'S3': 37.68,
                             'S4': 55.53,
                             'S5': 73.67,
                             'S6': 91.76,
                             'S7': 109.71,
                             'S8': 127.70,
                             'S9': 145.68,
                             'S10': 163.70,
                            },
                  fallback = 0,
                  fmtstr = '%s',
                  precision = 0.05,
                  blockingmove = False,
                  lowlevel = False,
                  unit = '',
                 ),
)
display_order = 60

alias_config = {
}
