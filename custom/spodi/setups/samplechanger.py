description = 'CARESS HWB Devices'

group = 'optional'

servername = 'VMESPODI'

nameservice = 'spodisrv.spodi.frm2'

includes = []

devices = dict(
    samsm = device('devices.vendor.caress.Motor',
                  description = 'HWB SAMS',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = -38613.,
                  abslimits = (-360, 360),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'SAMS 114 11 0x00f1e000 4 409 2000 100 2 24 50 '
                           '-1 0 1 4000 1 10 10 0 0',
                  lowlevel = True,
                 ),
    # Sample changer ***Attention SAMR is also CHIT (Load Frame Chi)***
    samr = device('devices.vendor.caress.Motor',
                  description = 'HWB SAMR',
                  fmtstr = '%.2f',
                  unit = 'deg',
                  coderoffset = 0,
                  abslimits = (-360, 360),
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'SAMR 115 11 0x00f1d000 1 644 10000 1000 1 0 50 '
                           '1 0 1 4000 1 10 10 0 0',
                 ),
    sams = device('devices.generic.Switcher',
                  description = 'Sample Changer drum',
                  moveable = 'samsm',
                  mapping = {'S1': 0.53,
                             'S2': 36.28,
                             'S3': 72.16,
                             'S4': 108.00,
                             'S5': 144.10,
                             'S6': 180.59,
                             'S7': 216.66,
                             'S8': 252.41,
                             'S9': 288.56,
                             'S10': 324.50,
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
