description = 'Measuring thermal conductivity'

group = 'optional'

includes = ['voltmeter2_direct', 'voltmeter_keysight', 'alias_T', 'busk6221']

sysconfig = dict(
    datasinks = ['rawsink', 'filesink', 'dmnsink'],
)

devices = dict(
    Cond = device('nicos_mgml.devices.conductivity.Conductivity',
        description = 'Conductivity',
        fmtstr = '%.8f',
        seebeck = 'VoltageSeebeckDev',
        voltage = 'VoltageDev',
        k6221 = 'busk6221',
        temp = 'T',
    ),
    CondCurrent = device('nicos.devices.generic.ParamDevice',
        description = 'current applied during conductivity measurement',
        device = 'Cond',
        parameter = 'current',
    ),
    rawsink = device('nicos.devices.datasinks.AsciiScanfileSink',
        settypes = ['subscan'],
        filenametemplate = ['%(scanpropcounter)08d.dat'],
        subdir = 'raw',
    ),

)

startupcode = '''
printinfo("Disabling deamonsink for subscans")
dmnsink._setROParam('settypes',frozenset({'scan'}))
'''

