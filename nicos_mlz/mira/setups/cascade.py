description = 'CASCADE detector (Tango version)'
group = 'lowlevel'

includes = ['detector', 'gas']
excludes = ['cascade_win']

tango_base = 'tango://miractrl.mira.frm2:10000/mira/'

sysconfig = dict(
    datasinks = ['psd_padformat', 'psd_tofformat', 'psd_xmlformat',
                 'psd_liveview'],
)

ARMING_STRING = (':TRIG1:SOUR BUS;'
                ':TRIG1:SLOP POS;'
                ':SOUR1:FUNC SQU;'
                ':OUTP1:LOAD +5.000000000000000E+01;'
                ':SOUR1:VOLT:UNIT VPP;'
                ':SOUR1:VOLT +5.0000000000000E+00;'
                ':SOUR1:VOLT:OFFS +2.5000000000000E+00;'
                ':SOUR1:FREQ:MODE CW;'
                ':SOUR1:VOLT:LIM:HIGH +5.000000000000000E+00;'
                ':SOUR1:VOLT:LIM:LOW -5.000000000000000E+00;'
                ':SOUR1:VOLT:LIM:STAT ON;'
                ':SOUR1:VOLT:RANG:AUTO 1;'
                ':SOUR1:ROSC:SOUR:AUTO ON;'
                ':SOUR1:BURS:MODE TRIG;'
                ':SOUR1:BURS:NCYC 9.9E37;'
                ':SOUR1:BURS:STAT ON;'
                ':SOUR1:BURS:PHAS +0.0000000000000E+00;'
                ':OUTP:MODE NORM;'
                ':OUTP:TRIG:SOUR CH1;'
                ':OUTP:TRIG:SLOP POS;'
                ':OUTP:TRIG 1;'
                ':OUTP1 ON;'
                ':SYST:BEEP:STAT ON;'
                ':TRIG2:SOUR BUS;'
                ':TRIG2:SLOP POS;'
                ':SOUR2:FUNC SQU;'
                ':OUTP2:LOAD +5.000000000000000E+01;'
                ':SOUR2:VOLT:UNIT VPP;'
                ':SOUR2:VOLT +5.0000000000000E+00;'
                ':SOUR2:VOLT:OFFS +2.5000000000000E+00;'
                ':SOUR2:FREQ:MODE CW;'
                ':SOUR2:VOLT:LIM:HIGH +5.000000000000000E+00;'
                ':SOUR2:VOLT:LIM:LOW -5.000000000000000E+00;'
                ':SOUR2:VOLT:LIM:STAT ON;'
                ':SOUR2:VOLT:RANG:AUTO 1;'
                ':SOUR2:BURS:MODE TRIG;'
                ':SOUR2:BURS:NCYC 9.9E37;'
                ':SOUR2:BURS:STAT ON;'
                ':SOUR2:BURS:PHAS +0.0000000000000E+00;'
                ':OUTP2 ON;')

TRG_STRING = ('*TRG')


devices = dict(
    fg_burst = device('nicos_mlz.devices.io_trigger.Trigger',
        description = "device for firing the multiburst option on the cascade " \
                      "driving frequency generator",
        tangodevice = tango_base + 'cascade/fg_io',
        safesetting = 'idle',
        strings = {'idle' : '',
                   'arm' : ARMING_STRING,
                   'trigger' : TRG_STRING,
                   }
        ),

    psd_padformat = device('nicos_mlz.reseda.devices.cascade.CascadePadSink',
        subdir = 'cascade',
        detectors = ['psd', 'counter', 'timer', 'monitor1', 'monitor2'],
    ),
    psd_tofformat = device('nicos_mlz.reseda.devices.cascade.CascadeTofSink',
        subdir = 'cascade',
        detectors = ['psd', 'counter', 'timer', 'monitor1', 'monitor2'],
    ),
    psd_liveview = device('nicos.devices.datasinks.LiveViewSink',
    ),
    psd_xmlformat = device('nicos_mlz.mira.devices.cascade.MiraXmlSink',
        subdir = 'cascade',
        timer = 'timer',
        monitor = 'mon2',
        sampledet = 'sampledet',
        mono = 'mono',
    ),
    psd_channel = device('nicos_mlz.reseda.devices.cascade.CascadeDetector',
        description = 'CASCADE detector channel',
        tangodevice = tango_base + 'cascade/tofchannel',
        foilsorder = [7, 6, 5, 0, 1, 2],
    ),
    psd = device('nicos.devices.generic.Detector',
        description = 'CASCADE detector',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        images = ['psd_channel'],
    ),
    psd_chop_freq = device('nicos.devices.tango.AnalogOutput',
        description = 'Chopper Frequency generator',
        tangodevice = tango_base + 'cascade/chop_freq',
        pollinterval = 30,
        fmtstr = '%.3f'
    ),
    psd_timebin_freq = device('nicos.devices.tango.AnalogOutput',
        description = 'Timebin Frequency generator',
        tangodevice = tango_base + 'cascade/timebin_freq',
        pollinterval = 30,
    ),
    PSDHV = device('nicos_mlz.mira.devices.iseg.CascadeIsegHV',
        description =
        'high voltage supply for the CASCADE detector (usually -2850 V)',
        tangodevice = tango_base + 'psdhv/voltage',
        abslimits = (-3100, 0),
        warnlimits = (-3000, -2945),
        pollinterval = 10,
        maxage = 20,
        fmtstr = '%d',
    ),
    co_dtx = device('nicos.devices.tango.Sensor',
        lowlevel = True,
        tangodevice = tango_base + 'detector/dtx_enc',
        unit = 'mm',
    ),
    mo_dtx = device('nicos.devices.tango.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'detector/dtx_mot',
        unit = 'mm',
        precision = 0.1,
    ),
    dtx = device('nicos.devices.generic.Axis',
        description = 'detector translation along the beam on Franke table',
        motor = 'mo_dtx',
        coder = 'co_dtx',
        fmtstr = '%.1f',
        precision = 0.1,
    ),
    sampledet = device('nicos.devices.generic.ManualMove',
        description = 'sample-detector distance to be written to the data files',
        abslimits = (0, 5000),
        unit = 'mm',
    ),
)
