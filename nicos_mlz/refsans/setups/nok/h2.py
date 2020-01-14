description = 'Slit H2 using Beckhoff controllers'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    h2_center = device(code_base + 'beckhoff.nok.BeckhoffMotorHSlit',
        description = 'Horizontal slit system: offset of the slit-center to the beam. towards TOFTOF is plus',
        tangodevice = tango_base + 'h2/io/modbus',
        address = 0x3020+0*10, # word address
        slope = -1000,
        unit = 'mm',
        abslimits = (-69.5, 69.5),
    ),
    h2_width = device(code_base + 'beckhoff.nok.BeckhoffMotorHSlit',
        description = 'Horizontal slit system: opening of the slit',
        tangodevice = tango_base + 'h2/io/modbus',
        address = 0x3020+1*10, # word address
        slope = 1000,
        unit = 'mm',
        abslimits = (0.05, 69.5),
    ),
)
