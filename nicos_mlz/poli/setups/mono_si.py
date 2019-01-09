description = 'POLI silicon monochromator devices'

group = 'optional'

excludes = ['mono_cu']

tango_base = 'tango://phys.poli.frm2:10000/poli/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    sih = device('nicos.devices.tango.Motor',
        lowlevel = False,
        description = 'Silicon monochromator horizontal focus',
        tangodevice = s7_motor + 'sih',
        fmtstr = '%.2f',
    ),
    siv = device('nicos.devices.tango.Motor',
        lowlevel = False,
        description = 'Silicon monochromator vertical focus',
        tangodevice = s7_motor + 'siv',
        fmtstr = '%.2f',
    ),
)
