description = 'CASCADE detector (Windows server version)'
group = 'lowlevel'

includes = ['detector']

sysconfig = dict(datasinks = ['psd_padformat', 'psd_liveview'],)

devices = dict(
    psd_padformat = device('mira.cascade.CascadePadSink',
        subdir = 'cascade',
        lowlevel = True,
    ),
    psd_liveview = device('devices.datasinks.LiveViewSink',
        lowlevel = True,
    ),
    psd_channel = device('mira.cascade_win.CascadeDetector',
        description = 'CASCADE detector channel',
        server = 'resedacascade02.reseda.frm2:1234',
    ),
    psd = device('devices.generic.Detector',
        description = 'CASCADE detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        images = ['psd_channel'],
    ),
)
