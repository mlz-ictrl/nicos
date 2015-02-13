description = 'SANS mode with PSD detector'
group = 'basic'

includes = ['detector', 'mono2', 'gas']

devices = dict(
    psd_padformat = device('mira.cascade.CascadePadRAWFormat',
                           lowlevel = True,
                          ),
    psd_tofformat = device('mira.cascade.CascadeTofRAWFormat',
                           lowlevel = True,
                          ),
    psd_xmlformat = device('mira.cascade.MiraXMLFormat',
                           master = 'det',
                           sampledet = 'sampledet',
                           mono = 'mono',
                           lowlevel = True,
                          ),
    psd_liveview  = device('devices.fileformats.liveview.LiveViewSink',
                           lowlevel = True,
                          ),

    psd    = device('mira.cascade.CascadeDetector',
                    description = 'CASCADE detector',
                    subdir = 'cascade',
                    server = 'miracascade.mira.frm2:1234',
                    slave = True,
                    master = 'det',
                    fileformats = ['psd_padformat', 'psd_tofformat',
                                   'psd_xmlformat', 'psd_liveview'],
                   ),

    PSDHV  = device('mira.iseg.CascadeIsegHV',
                    description = 'High voltage supply for the CASCADE detector (usually -2850 V)',
                    tacodevice = '//mirasrv/mira/network/rs12_4',
                    abslimits = (-3100, 0),
                    warnlimits = (-3100, -2800),
                    pollinterval = 10,
                    maxage = 20,
                    channel = 1,
                    unit = 'V',
                    fmtstr = '%d',
                   ),

    dtx    = device('mira.phytron.Axis',
                    description = 'Detector translation along the beam on Franke table',
                    tacodevice = '//mirasrv/mira/axis/dtx',
                    fmtstr = '%.1f',
                    abslimits = (0, 1490),
                    pollinterval = 5,
                    maxage = 10,
                   ),

    sampledet = device('devices.generic.ManualMove',
                       description = 'Sample-detector distance to be written to the data files',
                       abslimits = (0, 5000),
                       unit = 'mm',
                      ),
)
