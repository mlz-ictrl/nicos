description = 'POLI silicon monochromator'

group = 'lowlevel'

includes = ['mono', ]

excludes = ['mono_cu', ]

nethost = 'slow.poli.frm2'

devices = dict(
    bmv = device('devices.taco.Motor',
                 description = 'Monochromator vertical opening slit',
                 tacodevice = '//%s/poli/fzjs7/bmv' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (0, 10),
                 lowlevel = True,
                ),
    bmh = device('devices.taco.Motor',
                 description = 'Monochromator horizontal opening slit',
                 tacodevice = '//%s/poli/fzjs7/bmh' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (0, 10),
                 lowlevel = True,
                ),
    bm  = device('devices.generic.TwoAxisSlit',
                 description = 'Monochromator slit',
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f %.2f',
                 horizontal = 'bmh',
                 vertical = 'bmv',
                ),
)

startupcode = """
"""
