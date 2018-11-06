description = 'frequency counter, fg1 and fg2'

includes = []

excludes = ['frequency']

# group = 'lowlevel'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/tisane'

ARMING_STRING_FC = (
                ':FUNC "FREQ";'
                ':CALC:AVER 1;'
                ':CALC:SMO:RESP FAST;'
                ':CALC:SMO 1;'
                ':INP:COUP AC;'
                ':INP:FILT 0;'
                ':INP:IMP +1.00000000E+006;'
                ':INP:LEV -1.80000000E+000;'
                ':INP:LEV:REL +50;'
                ':INP:LEV:AUTO 0;'
                ':INP:NREJ 1;'
                ':INP:PROB +1;'
                ':INP:RANG +5.00000000E+000;'
                ':INP:SLOP POS;'
                ':MMEM:CDIR "INT:\\";'
                ':OUTP:POL NORM;'
                ':OUTP 0;'
                ':SAMP:COUN +1;'
                ':FREQ:GATE:POL NEG;'
                ':FREQ:GATE:SOUR TIME;'
                ':FREQ:GATE:TIME +1.00000000000000E-001;'
                ':TRIG:COUN +1;'
                ':TRIG:DEL +0.00000000000000E+000;'
                ':TRIG:SLOP NEG;'
                ':TRIG:SOUR IMM;'
                 )
ARMING_STRING = (
                '*RST;'

                ':SOUR1:FUNC:SHAP SQU;'
                ':SOUR1:FREQ 5;'
                ':SOUR1:VOLT 2.4;'
                ':SOUR1:VOLT:UNIT VPP;'
                ':SOUR1:VOLT:OFFS 1.3;'
                ':SOUR1:FUNCtion:SQU:DCYCle 50;'
                ':SOUR1:AM:STATe OFF;'
                ':SOUR1:SWEep:STATe OFF;'
                ':SOUR1:BURSt:MODE TRIG;'
                ':OUTP1:LOAD 50;'
                ':OUTP1:POL NORM;'
                ':TRIG1:SOUR EXT;'
                ':SOUR1:BURSt:NCYCles 9.9E37;'

                ':SOUR2:FUNC:SHAP SQU;'
                ':SOUR2:FREQ 10;'
                ':SOUR2:VOLT 5;'
                ':SOUR2:VOLT:UNIT VPP;'
                ':SOUR2:VOLT:OFFS 1.3;'
                ':SOUR2:FUNCtion:SQU:DCYCle 50;'
                ':SOUR2:AM:STATe OFF;'
                ':SOUR2:SWEep:STATe OFF;'
                ':SOUR2:BURSt:MODE TRIG;'
                ':OUTP2:LOAD 50;'
                ':OUTP2:POL NORM;'
                ':TRIG2:SOUR EXT;'
                ':SOUR2:BURSt:NCYCles 9.9E37;'


                ':SOUR1:BURSt:STATe ON;'
                ':SOUR2:BURSt:STATe ON;'
                ':OUTP1 ON;'
                ':OUTP2 ON;'
                 )
OFF_STRING = (
                ':OUTP1 OFF;'
                ':OUTP2 OFF;'
                ':SOUR1:BURSt:STATe OFF;'
                ':SOUR2:BURSt:STATe OFF;'
                 )

devices = dict(
    tisane_fc = device('nicos.devices.tango.Sensor',
        description = "Frequency counter for chopper signal",
        tangodevice = "%s/fc1_frequency" % tango_base,
        unit = "Hz",
        pollinterval = 1,
        fmtstr = '%.6f',
    ),
    tisane_fc_trigger = device('nicos_mlz.devices.io_trigger.Trigger',
        description = "String blasting device",
        tangodevice = "%s/fc1_io" % tango_base,
        lowlevel = True,
        safesetting = 'idle',
        strings = {'idle' : '',
                   'arm' : ARMING_STRING_FC,
                  }
        ),
#    tisane_fg1_sample = device('nicos_mlz.sans1.devices.tisane.Burst',
#        description = "Signal-generator for sample tisane signal",
#        tangodevice = "%s_multifg/ch1_burst" % tango_base,
#        frequency = 1000,
#        amplitude = 2.5,
#        offset = 1.3,
#        shape = 'square',
#        duty = 50,
#        mapping = dict(On = 1, Off = 0),
#    ),
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

    tisane_fg_multi = device('nicos_mlz.devices.io_trigger.Trigger',
        description = "String blasting device",
        tangodevice = "%s_multifg/io" % tango_base,
        safesetting = 'idle',
        strings = {'idle' : '',
                   'arm' : ARMING_STRING,
                   'off' : OFF_STRING,
                  }
        ),
)
