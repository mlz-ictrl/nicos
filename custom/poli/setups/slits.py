description = 'POLI silicon monochromator'

group = 'lowlevel'

includes = ['mono', ]

excludes = []

tango_host = 'tango://phys.poli.frm2:10000'

devices = dict(
    bmv = device('devices.tango.Motor',
                 description = 'Monochromator vertical opening slit',
                 tangodevice = '%s/poli/fzjs7/bmv' % (tango_host, ),
                 fmtstr = '%.2f',
                 abslimits = (114, 190),
                 precision = 0.2,
                 lowlevel = False,
                ),
    bmh = device('devices.tango.Motor',
                 description = 'Monochromator horizontal opening slit',
                 tangodevice = '%s/poli/fzjs7/bmh' % (tango_host, ),
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
