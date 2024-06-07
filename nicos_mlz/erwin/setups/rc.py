description = 'Radial collimator devices'

group = 'lowlevel'

devices = dict(
    rc = device('nicos_mlz.erwin.devices.rc.RadialCollimator',
        description = 'Radial collimator',
        motor = 'rc_motor',
    ),
    rc_motor = device('nicos.devices.entangle.Motor',
        description = 'Radial collimator motor',
        tangodevice = 'tango://motorbox02.erwin.frm2.tum.de:10000/box/channel7/motor',
    ),
)
