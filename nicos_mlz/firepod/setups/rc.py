description = 'Radial collimator devices'

group = 'lowlevel'

devices = dict(
    # rc = device('nicos_mlz.erwin.devices.rc.RadialCollimator',
    rc = device('nicos.devices.generic.ManualSwitch',
        description = 'Radial collimator',
        states = ['off', 'on'],
    #     motor = 'rc_motor',
    ),
    # rc_motor = device('nicos.devices.entangle.Motor',
    #     description = 'Radial collimator motor',
    #     tangodevice = 'tango://motorbox02.firepod.frm2.tum.de:10000/box/channel7/motor',
    # ),
)
