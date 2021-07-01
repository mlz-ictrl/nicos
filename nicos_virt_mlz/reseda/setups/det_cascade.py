description = 'CASCADE detector'

group = 'lowlevel'

includes = ['det_base', 'filesavers', 'mono']

excludes = ['det_3he']

sysconfig = dict(
    datasinks = ['psd_padformat', 'psd_tofformat', 'psd_liveview',
                 'psd_xmlformat', 'HDF5FileSaver'],
)

devices = dict(
    fg_burst = device('nicos.devices.generic.ManualSwitch',
        description = 'String blasting device',
        states = ['idle', 'arm', 'trigger'],
        fmtstr = '%s',
        unit = '',
    ),
    psd_padformat = device('nicos.devices.vendor.cascade.CascadePadSink',
        subdir = 'cascade',
        detectors = ['psd', 'scandet', 'counter', 'timer', 'monitor1', 'monitor2'],
    ),
    psd_tofformat = device('nicos.devices.vendor.cascade.CascadeTofSink',
        subdir = 'cascade',
        detectors = ['psd', 'scandet', 'counter', 'timer', 'monitor1', 'monitor2'],
    ),
    psd_liveview = device('nicos.devices.datasinks.LiveViewSink'),
    sampledet = device('nicos.devices.generic.ManualMove',
        description = 'sample-detector distance to be written to the data files',
        abslimits = (0, 5000),
        unit = 'mm',
    ),
    psd_xmlformat = device('nicos_mlz.mira.devices.cascade.MiraXmlSink',
        subdir = 'cascade',
        timer = 'timer',
        monitor = 'monitor1',
        sampledet = 'sampledet',
        mono = 'vmono',
    ),
    psd_channel = device('nicos_virt_mlz.reseda.devices.CascadeDetector',
        description = 'CASCADE detector channel',
        foilsorder = [5, 4, 3, 0, 1, 2, 6, 7],
    ),
    psd = device('nicos.devices.generic.Detector',
        description = 'CASCADE detector',
        timers = ['timer'],
        monitors = ['monitor1'],
        images = ['psd_channel'],
    ),
    psd_distance = device('nicos.devices.generic.ManualMove',
        description = 'Sample-Detector Distance L_sd',
        abslimits = (0, 4),
        default = 3.43,
        unit = 'm',
    ),
    psd_chop_freq = device('nicos.devices.generic.ManualMove',
        description = 'Chopper Frequency generator',
        pollinterval = 30,
        fmtstr = '%.3f',
        abslimits = (0.1, 1e7),
        default = 30000,
        unit = 'Hz',
    ),
    psd_timebin_freq = device('nicos.devices.generic.ManualMove',
        description = 'Timebin Frequency generator',
        pollinterval = 30,
        fmtstr = '%.3f',
        abslimits = (0.1, 1e7),
        default = 10000,
        unit = 'Hz',
    ),
    det_hv = device('nicos.devices.generic.ManualMove',
        description = 'High voltage power supply of the 3he detector',
        abslimits = (-3000, 0),
        warnlimits = (-3000, -2800),
        pollinterval = 10,
        maxage = 20,
        fmtstr = '%.f',
        unit = 'V',
        default = 0,
    ),
)


startupcode = '''
# SetDetectors(psd)
# psd_channel.mode='tof'
'''
