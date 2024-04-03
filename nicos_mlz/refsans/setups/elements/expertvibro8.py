description = f'{setupname} readout devices'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + f'{setupname}/io/modbus'
code_base = instrument_values['code_base'] + f'{setupname}.'

devices = dict(
)

for i in range(1, 5):
    devices[f'{setupname}_trigger_{i}'] = device(code_base + 'AnalogValue',
        description = f'{setupname} Trigger {i}',
        tangodevice = tango_base,
        channel = 0 + (i -1) * 4,
    )
    devices[f'{setupname}_Amplitude_{i}'] = device(code_base + 'AnalogValue',
        description = f'{setupname} Amplitude {i}',
        tangodevice = tango_base,
        channel = 1 + (i - 1) * 4,
    )
    devices[f'{setupname}_Phase_{i}'] = device(code_base + 'AnalogValue',
        description = f'{setupname} Phase {i}',
        tangodevice = tango_base,
        channel = 2 + (i - 1) * 4,
    )
    devices[f'{setupname}_Frequenz_{i}'] = device(code_base + 'AnalogValue',
        description = f'{setupname} Frequenz {i}',
        tangodevice = tango_base,
        channel = 3 + (i - 1) * 4,
    )
