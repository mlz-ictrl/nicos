description = 'POLI silicon monochromator devices'

group = 'optional'

excludes = ['mono_cu']

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    sih = device('devices.tango.Motor',
                 lowlevel = False,
                 description = 'Silicon monochromator horizontal focus',
                 tangodevice = tango_base + 'fzjs7/sih',
                 fmtstr = '%.2f',
                ),
    siv = device('devices.tango.Motor',
                 lowlevel = False,
                 description = 'Silicon monochromator vertical focus',
                 tangodevice = tango_base + 'fzjs7/siv',
                 fmtstr = '%.2f',
                ),
)
