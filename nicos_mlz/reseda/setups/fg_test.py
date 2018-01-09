description = 'frequency generator for testing!'

includes = []

excludes = []

# group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda/cascade'

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
#    tisane_fg2_det = device('nicos_mlz.sans1.devices.tisane.Burst',
#        description = "Signal-generator for detector tisane signal",
#        tangodevice = "%s_multifg/ch2_burst" % tango_base,
#        frequency = 1000,
#        amplitude = 5.0,
#        offset = 1.3,
#        shape = 'square',
#        duty = 50,
#        mapping = dict(On = 1, Off = 0),
#    ),

    fg_test = device('nicos_mlz.reseda.devices.io_trigger.Trigger',
        description = "String blasting device",
        tangodevice = "%s/io_fg" % tango_base,
        safesetting = 'idle',
        strings = {'idle' : '',
                   'arm' : ARMING_STRING,
                   'trigger' : TRG_STRING,
                   }
        ),
)
