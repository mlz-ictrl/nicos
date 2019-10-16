description = 'Sample slit devices'

group = 'plugplay'

tangobase = 'tango://motorbox01.stressi.frm2.tum.de:10000/box/'

devices = dict(
    slits_d = device('nicos.devices.tango.Motor',
        description = 'Bottom blade of sample slit',
        tangodevice = tangobase + 'channel2/motor',
        lowlevel = True,
    ),
    slits_u = device('nicos.devices.tango.Motor',
        description = 'Upper blade of the sample slit',
        tangodevice = tangobase + 'channel1/motor',
        lowlevel = True,
    ),
    slits_l = device('nicos.devices.tango.Motor',
        description = 'Left blade of the sample slit',
        tangodevice = tangobase + 'channel3/motor',
        lowlevel = True,
    ),
    slits_r = device('nicos.devices.tango.Motor',
        description = 'Right blade of the sample slit',
        tangodevice = tangobase + 'channel4/motor',
        lowlevel = True,
    ),
)
