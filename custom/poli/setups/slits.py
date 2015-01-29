description = 'POLI silicon monochromator'

group = 'lowlevel'

includes = ['mono', ]

excludes = []

nethost = 'slow.poli.frm2'

devices = dict(
    bmv = device('devices.taco.Motor',
                 description = 'Monochromator vertical opening slit',
                 tacodevice = '//%s/poli/fzjs7/bmv' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (114, 190),
                 precision = 0.2,
                 lowlevel = False,
                ),
    bmh = device('devices.taco.Motor',
                 description = 'Monochromator horizontal opening slit',
                 tacodevice = '//%s/poli/fzjs7/bmh' % (nethost, ),
                 pollinterval = 15,
                 maxage = 61,
                 fmtstr = '%.2f',
                 abslimits = (6.5, 80),
                 precision = 0.2,
                 lowlevel = False,
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
