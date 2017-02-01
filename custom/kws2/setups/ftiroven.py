description = 'Oven used for the Fourier-transforming infrared spectrometer'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    T_ftir = device('devices.tango.TemperatureController',
                    description = 'The regulated temperature',
                    tangodevice = tango_base + 'ftiroven/control',
                    abslimits = (-190, 200),
                    unit = 'degC',
                    fmtstr = '%.2f',
                    precision = 2.0,
                    timeout = 1800.0,
                   ),
)

alias_config = {
    'T':  {'T_ftir': 110},
    'Ts': {'T_ftir': 110},
}
