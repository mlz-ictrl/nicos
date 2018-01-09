description = 'CASCADE detector (Windows server version)'
group = 'lowlevel'
includes = ['det_base']
excludes = ['det_3he']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

sysconfig = dict(
    datasinks = ['psd_padformat', 'psd_tofformat', 'psd_liveview', 'HDF5FileSaver'],
)

devices = dict(
#    scandet = device('nicos.devices.generic.ScanningDetector',
    scandet = device('nicos_mlz.reseda.devices.scandet.ScanningDetector',
        description = 'Scanning detector for scans per echotime',
        scandev = 'nse0',
        detector = 'psd',
        maxage = 2,
        pollinterval = 0.5,
    ),
    psd_padformat = device('nicos_mlz.mira.devices.cascade.CascadePadSink',
        subdir = 'cascade',
        lowlevel = True,
    ),
    psd_tofformat = device('nicos_mlz.mira.devices.cascade.CascadeTofSink',
        subdir = 'cascade',
        lowlevel = True,
    ),
    psd_liveview = device('nicos.devices.datasinks.LiveViewSink',
        lowlevel = True,
    ),
    psd_channel = device('nicos_mlz.mira.devices.cascade_win.CascadeDetector',
        description = 'CASCADE detector channel',
        server = 'resedacascade02.reseda.frm2:1234',
        slave = False,
    ),
    psd = device('nicos.devices.generic.Detector',
        description = 'CASCADE detector',
        timers = ['timer'],
        monitors = ['monitor1', 'monitor2'],
        images = ['psd_channel'],
    ),
    psd_distance = device('nicos.devices.generic.virtual.VirtualMotor',
        description = 'Sample-Detector Distance L_sd',
        abslimits = (0, 4),
        unit = 'm',
    ),
    psd_chop_freq = device('nicos.devices.tango.AnalogOutput',
            description = 'Chopper Frequency generator',
            tangodevice = '%s/cascade/chop_freq' % (tango_base), 
            pollinterval = 3,
            fmtstr = '%.3g'
        ),
   psd_timebin_freq = device('nicos.devices.tango.AnalogOutput',
            description = 'Timebin Frequency generator',
            tangodevice = '%s/cascade/timebin_freq' % (tango_base),
            pollinterval = 3,
        ),

    #psd_fg_onoff = device('nicos.devices.tango.OnOffSwitch',
    #    description = 'FG output on/off switch',
    #    tangodevice = '%s/cascade/timebin_freq' % (tango_base),
    #    ),
    #psd_chop_burst = device('nicos.devices.tango.NamedDigitalOutput',
    #        description = 'Burst Chopper Signal',
    #        tangodevice = '%s/cascade/chop_burst' % (tango_base),
    #        mapping = {'On':1, 'Off':0},
    #    ),
    #psd_timebin_burst = device('nicos.devices.tango.NamedDigitalOutput',
    #        description = 'Burst Timebin Signal',
    #        tangodevice = '%s/cascade/timebin_burst' % (tango_base),
    #        mapping = {'On':1, 'Off':0},
    #    ),
    )

startupcode = '''
SetDetectors(scandet)
'''
