description = 'CASCADE detector (Windows server version)'
group = 'lowlevel'
includes = ['det_base']
excludes = ['det_3he']

sysconfig = dict(
    datasinks = ['psd_padformat', 'psd_liveview', 'HDF5FileSaver'],
)

devices = dict(
    scandet = device('nicos.devices.generic.ScanningDetector',
        description = 'Scanning detector for scans per echotime',
        scandev = 'subcoil_ps2',
        detector = 'psd',
        maxage = 2,
        pollinterval = 0.5,
    ),
    psd_padformat = device('nicos_mlz.mira.devices.cascade.CascadePadSink',
        subdir = 'cascade',
        lowlevel = True,
    ),
    psd_liveview = device('nicos.devices.datasinks.LiveViewSink',
        lowlevel = True,
    ),
    psd_channel = device('nicos_mlz.mira.devices.cascade_win.CascadeDetector',
        description = 'CASCADE detector channel',
        server = 'resedacascade02.reseda.frm2:1234',
    ),
    psd = device('nicos.devices.generic.Detector',
        description = 'CASCADE detector',
        timers = ['timer'],
        monitors = ['monitor1', 'monitor2'],
        images = ['psd_channel'],
    ),
)

startupcode = '''
SetDetectors(scandet)
'''
