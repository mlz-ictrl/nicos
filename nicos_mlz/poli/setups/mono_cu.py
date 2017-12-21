description = 'POLI copper monochromator devices'

group = 'optional'

excludes = ['mono_si']

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    cuh = device('nicos.devices.tango.Motor',
        lowlevel = False,
        description = 'Copper monochromator horizontal focus',
        tangodevice = tango_base + 'fzjs7/cuh',
        fmtstr = '%.2f',
    ),
    cuv = device('nicos.devices.tango.Motor',
        lowlevel = False,
        description = 'Copper monochromator vertical focus',
        tangodevice = tango_base + 'fzjs7/cuv',
        fmtstr = '%.2f',
    ),
)
