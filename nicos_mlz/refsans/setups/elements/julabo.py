description = 'REFSANS setup for julabo01 Presto A40'

group = 'optional'

includes = ['ana4gpio01']

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'refsans/julabo01/'
code_base = instrument_values['code_base']

devices = dict(
    julabo_temp = device('nicos.devices.entangle.TemperatureController',
        description = 'Julabo01 temperature control',
        tangodevice = tango_base + 'control',
        fmtstr = '%.2f',
    ),
    julabo_int = device('nicos.devices.entangle.Sensor',
        description = 'Julabo01 temperature bath',
        tangodevice = tango_base + 'intsensor',
        fmtstr = '%.2f',
    ),
    julabo_ext = device('nicos.devices.entangle.Sensor',
        description = 'Julabo01 external sensor',
        tangodevice = tango_base + 'extsensor',
        fmtstr = '%.2f',
    ),
    julabo_flow = device(code_base + 'analogencoder.AnalogEncoder',
        description = 'flow of julabo at PO by Sensor',
        device = 'ana4gpio01_ch2',
        poly = [0, 30.10],  #10V = 100L/min Spannungsteiler 10V/(5110+2200)*2200=3,01V
        unit = 'L/min',
    ),
    julabo_flow_avg = device(code_base + 'avg.BaseAvg',
        description = 'avg for flow',
        dev = 'julabo_flow',
        unit = 'L/min',
    ),
)
