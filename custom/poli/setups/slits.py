description = 'POLI silicon monochromator'

group = 'lowlevel'

includes = ['mono', ]

excludes = []

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    bmv = device('devices.tango.Motor',
                 description = 'Monochromator vertical opening slit',
                 tangodevice = tango_base + 'fzjs7/bmv',
                 fmtstr = '%.2f',
                 abslimits = (114, 190),
                 precision = 0.2,
                 lowlevel = False,
                ),
    bmh = device('devices.tango.Motor',
                 description = 'Monochromator horizontal opening slit',
                 tangodevice = tango_base + 'fzjs7/bmh',
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
