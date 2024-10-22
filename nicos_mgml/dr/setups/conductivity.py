description = 'Measuring thermal conductivity'

group = 'optional'

includes = ['voltage', 'voltage2']

devices = dict(

    Cond = device('nicos_mgml.devices.conductivity.Conductivity',
        description = 'Conductivity',
        fmtstr = '%.8f',
        seebeck = 'VoltageDevSeebeck',
        voltage = 'VoltageDev',
        temp = 'T_ppms',
    ),

    CondCurrent = device('nicos.devices.generic.ParamDevice',
        description = 'current applied during conductivity measurement',
        device = 'Cond',
        parameter = 'current',
    ),
)
