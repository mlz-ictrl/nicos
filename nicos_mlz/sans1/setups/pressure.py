description = 'Vacuum sensors of detector and collimation tube'

group = 'lowlevel'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1'

devices = dict(
    det_tube = device('nicos.devices.entangle.Sensor',
        description = 'pressure detector tube: Tube',
        tangodevice = tango_base + '/tube/p1',
        fmtstr = '%.4G',
        pollinterval = 15,
        maxage = 60,
        warnlimits = (0, 1),
        lowlevel = True,
    ),
    det_nose = device('nicos.devices.entangle.Sensor',
        description = 'pressure detector tube: Nose',
        tangodevice = tango_base + '/tube/p2',
        fmtstr = '%.4G',
        pollinterval = 15,
        maxage = 60,
        warnlimits = (0, 1),
        lowlevel = True,
    ),
    coll_tube = device('nicos.devices.entangle.Sensor',
        description = 'pressure collimation tube: Tube',
        tangodevice = tango_base + '/collimation/p1',
        fmtstr = '%.4G',
        pollinterval = 15,
        maxage = 60,
        warnlimits = (0, 1),
        lowlevel = True,
    ),
    coll_nose = device('nicos.devices.entangle.Sensor',
        description = 'pressure collimation tube: Nose',
        tangodevice = tango_base + '/collimation/p2',
        fmtstr = '%.4G',
        pollinterval = 15,
        maxage = 60,
        warnlimits = (0, 1),
        lowlevel = True,
    ),
)
