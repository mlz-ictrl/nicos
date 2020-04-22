description = 'CASCADE detector'
group = 'lowlevel'
includes = ['det_base']
excludes = ['det_3he', 'det_cascade2']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda/'

sysconfig = dict(
    datasinks = ['psd_padformat', 'psd_tofformat', 'psd_liveview', 'HDF5FileSaver'],
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
    # scandet = device('nicos_mlz.reseda.devices.scandet.ScanningDetector',
    #     description = 'Scanning detector for scans per echotime',
    #     scandev = 'nse0',
    #     detector = 'psd',
    #     maxage = 2,
    #     pollinterval = 0.5,
    # ),
    fg_burst = device('nicos_mlz.devices.io_trigger.Trigger',
        description = "String blasting device",
        tangodevice = tango_base + 'cascade/io_fg',
        safesetting = 'idle',
        strings = {'idle' : '',
                   'arm' : ARMING_STRING,
                   'trigger' : TRG_STRING,
                   }
        ),
    psd_padformat = device('nicos_mlz.reseda.devices.cascade.CascadePadSink',
        subdir = 'cascade',
        detectors = ['psd', 'scandet', 'counter', 'timer', 'monitor1', 'monitor2'],
    ),
    psd_tofformat = device('nicos_mlz.reseda.devices.cascade.CascadeTofSink',
        subdir = 'cascade',
        detectors = ['psd', 'scandet', 'counter', 'timer', 'monitor1', 'monitor2'],
    ),
    psd_liveview = device('nicos.devices.datasinks.LiveViewSink',
    ),
    psd_channel = device('nicos_mlz.reseda.devices.cascade.CascadeDetector',
        description = 'CASCADE detector channel',
        tangodevice = tango_base + 'cascade/tofchannel',
        tofchannels = 128,
        foilsorder = [5, 4, 3, 0, 1, 2, 6, 7],
    ),
    psd = device('nicos.devices.generic.Detector',
        description = 'CASCADE detector',
        timers = ['timer'],
        monitors = ['monitor1'],
        images = ['psd_channel'],
    ),
    psd_distance = device('nicos.devices.generic.virtual.VirtualMotor',
        description = 'Sample-Detector Distance L_sd',
        abslimits = (0, 4),
        unit = 'm',
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
    det_hv = device('nicos.devices.tango.PowerSupply',
        description = 'High voltage power supply of the Cascade detector',
        tangodevice = tango_base + 'cascade/hv',
        abslimits = (-3000, 0),
        warnlimits = (-3000, -2700),
        pollinterval = 10,
        maxage = 20,
        fmtstr = '%.f',
    ),
)


startupcode = '''
SetDetectors(psd)
psd_channel.mode='tof'
'''
