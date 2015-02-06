description = 'POLI silicon monochromator devices'

group = 'lowlevel'

tango_host = 'tango://localhost:10000'

devices = dict(
    sih = device('devices.tango.Motor',
                 lowlevel = False,
                 description = 'Silicon monochromator horizontal focus',
                 tangodevice = '%s/poli/fzjs7/sih' % (tango_host, ),
                 fmtstr = '%.2f',
                 abslimits = (0, 10),
                ),
    siv = device('devices.tango.Motor',
                 lowlevel = False,
                 description = 'Silicon monochromator vertical focus',
                 tangodevice = '%s/poli/fzjs7/siv' % (tango_host, ),
                 fmtstr = '%.2f',
                 abslimits = (0, 10),
                ),
)

startupcode = """
"""
