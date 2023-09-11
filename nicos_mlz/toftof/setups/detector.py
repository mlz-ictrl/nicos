description = 'TOF counter devices'

group = 'lowlevel'

tango_base = 'tango://cpci3.toftof.frm2.tum.de:10000/'

devices = dict(
    timer = device('nicos.devices.entangle.TimerChannel',
        description = 'The TOFTOF timer',
        tangodevice = tango_base + 'toftof/det/timer',
        fmtstr = '%.1f',
        visibility = (),
    ),
    monitor = device('nicos.devices.entangle.CounterChannel',
        description = 'The TOFTOF monitor',
        tangodevice = tango_base + 'toftof/det/monitor',
        type = 'monitor',
        presetaliases = ['mon1'],
        fmtstr = '%d',
        unit = 'cts',
        visibility = (),
    ),
    image = device('nicos_mlz.toftof.devices.TOFTOFChannel',
        description = 'The TOFTOF image',
        tangodevice = tango_base + 'toftof/det/histogram',
        timechannels = 1024,
        fmtstr = '%d',
        unit = 'cts',
        visibility = (),
    ),
    det = device('nicos_mlz.toftof.devices.Detector',
        description = 'The TOFTOF detector device',
        timers = ['timer'],
        monitors = ['monitor'],
        images = ['image'],
        rc = 'rc_onoff',
        chopper = 'ch',
        chdelay = 'chdelay',
        pollinterval = None,
        liveinterval = 10.0,
        saveintervals = [30.],
        detinfofile = '/control/nicos_mlz/toftof/detinfo.dat',
    ),
)
