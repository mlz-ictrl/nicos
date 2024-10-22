description = 'Measuring thermal conductivity'

group = 'optional'

includes = ['voltage', 'voltage2', 'alias_T', 'busk6221']

devices = dict(
    Cond = device('nicos_mgml.devices.conductivity.Conductivity',
        description = 'Conductivity',
        fmtstr = '%.8f',
        seebeck = 'VoltageDevSeebeck',
        voltage = 'VoltageDev',
        k6221 = 'busk6221gpib',
        temp = 'Ts',
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
conssink._setROParam('settypes',frozenset({'scan'}))
filesink._setROParam('settypes',frozenset({'scan'}))
'''
