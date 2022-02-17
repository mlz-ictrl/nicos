description = 'POLI copper monochromator devices'

group = 'optional'

excludes = ['mono_si']

tango_base = 'tango://phys.poli.frm2:10000/poli/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    cuh = device('nicos.devices.entangle.Motor',
        lowlevel = False,
        description = 'Copper monochromator horizontal focus',
        tangodevice = s7_motor + 'cuh',
        fmtstr = '%.2f',
    ),
    cuv = device('nicos.devices.entangle.Motor',
        lowlevel = False,
        description = 'Copper monochromator vertical focus',
        tangodevice = s7_motor + 'cuv',
        fmtstr = '%.2f',
    ),
    cuh_poti = device('nicos.devices.entangle.Sensor',
        lowlevel = False,
        description = 'Copper monochromator horizontal focus poti readout',
        tangodevice = tango_base + 's7_ios/cuh_poti',
    ),
    cuv_poti = device('nicos.devices.entangle.Sensor',
        lowlevel = False,
        description = 'Copper monochromator vertical focus poti readout',
        tangodevice = tango_base + 's7_ios/cuv_poti',
    ),
)
