description = 'CASCADE detector'
group = 'lowlevel'

includes = ['detector', 'gas']

devices = dict(
    psd_padformat = device('mira.cascade.CascadePadRAWFormat',
                           lowlevel = True,
                          ),
    psd_tofformat = device('mira.cascade.CascadeTofRAWFormat',
                           lowlevel = True,
                          ),
    psd_xmlformat = device('mira.cascade.MiraXMLFormat',
                           timer = 'timer',
                           monitor = 'mon2',
                           sampledet = 'sampledet',
                           mono = 'mono',
                           lowlevel = True,
                          ),
    psd_liveview  = device('devices.fileformats.liveview.LiveViewSink',
                           lowlevel = True,
                          ),

    psd_channel   = device('mira.cascade.CascadeDetector',
                           description = 'CASCADE detector channel',
                           server = 'miracascade.mira.frm2:1234',
                           slave = True,
                          ),

    psd    = device('devices.generic.Detector',
                    description = 'CASCADE detector',
                    subdir = 'cascade',
                    timers = ['timer'],
                    monitors = ['mon1', 'mon2'],
                    images = ['psd_channel'],
                    fileformats = ['psd_padformat', 'psd_tofformat',
                                   'psd_xmlformat', 'psd_liveview'],
                   ),

    PSDHV  = device('mira.iseg.CascadeIsegHV',
                    description = 'high voltage supply for the CASCADE detector (usually -2850 V)',
                    tangodevice = 'tango://mira1.mira.frm2:10000/mira/psdhv/voltage',
                    abslimits = (-3100, 0),
                    warnlimits = (-3000, -2945),
                    pollinterval = 10,
                    maxage = 20,
                    fmtstr = '%d',
                   ),

    dtx    = device('mira.phytron.Axis',
                    description = 'detector translation along the beam on Franke table',
                    tacodevice = '//mirasrv/mira/axis/dtx',
                    fmtstr = '%.1f',
                    abslimits = (0, 1490),
                    pollinterval = 5,
                    maxage = 10,
                   ),

    sampledet = device('devices.generic.ManualMove',
                       description = 'sample-detector distance to be written to the data files',
                       abslimits = (0, 5000),
                       unit = 'mm',
                      ),
)
