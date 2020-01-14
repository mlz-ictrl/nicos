description = 'pressure sensors connected to the chambers'

group = 'lowlevel'

includes = ['vsd']

instrument_values = configdata('instrument.values')

code_base = instrument_values['code_base'] + 'converters.Ttr'

devices = dict(
    chamber_CB = device(code_base,
        description = 'pressure sensor connected to the CB',
        unit = 'mbar',
        att = 'X16Voltage1',
    ),
    chamber_SFK = device(code_base,
        description = 'pressure sensor connected to the SFK',
        unit = 'mbar',
        att = 'X16Voltage2',
    ),
    chamber_SR = device(code_base,
        description = 'pressure sensor connected to the SR',
        unit = 'mbar',
        att = 'X16Voltage3',
    ),
)
