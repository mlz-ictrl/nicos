description = 'CASCADE detector (Tango version)'
group = 'lowlevel'

includes = ['detector', 'gas']
excludes = ['cascade_win']

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

sysconfig = dict(
    datasinks = ['psd_padformat', 'psd_tofformat', 'psd_xmlformat',
                 'psd_liveview'],
)

devices = dict(
    psd_padformat = device('nicos_mlz.mira.cascade.CascadePadSink',
                           subdir = 'cascade',
                           lowlevel = True,
                          ),
    psd_tofformat = device('nicos_mlz.mira.cascade.CascadeTofSink',
                           subdir = 'cascade',
                           lowlevel = True,
                          ),
    psd_xmlformat = device('nicos_mlz.mira.cascade.MiraXmlSink',
                           subdir = 'cascade',
                           timer = 'timer',
                           monitor = 'mon2',
                           sampledet = 'sampledet',
                           mono = 'mono',
                           lowlevel = True,
                          ),
    psd_liveview  = device('nicos.devices.datasinks.LiveViewSink',
                           lowlevel = True,
                          ),

    psd_channel   = device('nicos_mlz.mira.cascade.CascadeDetector',
                           description = 'CASCADE detector channel',
                           tangodevice = 'tango://cascade02.mira.frm2:10000/box/cascade/tofchannel',
                          ),

    psd           = device('nicos.devices.generic.Detector',
                           description = 'CASCADE detector',
                           timers = ['timer'],
                           monitors = ['mon1', 'mon2'],
                           images = ['psd_channel'],
                          ),

    PSDHV  = device('nicos_mlz.mira.iseg.CascadeIsegHV',
                    description = 'high voltage supply for the CASCADE detector (usually -2850 V)',
                    tangodevice = tango_base + 'psdhv/voltage',
                    abslimits = (-3100, 0),
                    warnlimits = (-3000, -2945),
                    pollinterval = 10,
                    maxage = 20,
                    fmtstr = '%d',
                   ),

    co_dtx   = device('nicos.devices.tango.Sensor',
                      lowlevel = True,
                      tangodevice = tango_base + 'detector/dtx_enc',
                      unit = 'mm',
                     ),
    mo_dtx   = device('nicos.devices.tango.Motor',
                      lowlevel = True,
                      tangodevice = tango_base + 'detector/dtx_mot',
                      unit = 'mm',
                      precision = 0.1,
                     ),
    dtx      = device('nicos.devices.generic.Axis',
                      description = 'detector translation along the beam on Franke table',
                      motor = 'mo_dtx',
                      coder = 'co_dtx',
                      obs = [],
                      fmtstr = '%.1f',
                      precision = 0.1,
                     ),

    sampledet = device('nicos.devices.generic.ManualMove',
                       description = 'sample-detector distance to be written to the data files',
                       abslimits = (0, 5000),
                       unit = 'mm',
                      ),
)
