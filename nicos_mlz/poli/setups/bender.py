description = 'POLI benderpolarizer'

group = 'optional'

tango_base = 'tango://phys.poli.frm2:10000/poli/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    bender_rot = device('nicos.devices.tango.Motor',
        description = 'SM polarizer rotation',
        tangodevice = s7_motor + 'bender_rot',
        fmtstr = '%.2f',
        abslimits = (-180, 180),
        precision = 0.2,
        lowlevel = False,
    ),
    bender_trans = device('nicos.devices.tango.Motor',
        description = 'SM polarizer translation',
        tangodevice = s7_motor + 'bender_trans',
        fmtstr = '%.2f',
        abslimits = (0, 200),
        precision = 0.2,
        lowlevel = False,
    ),
)
