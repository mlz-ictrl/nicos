description = 'Setup for New Era Syringe pumps'

group = 'optional'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base'] + 'syringepump.'

devices = dict(
    pump0_diameter = device('nicos.devices.tango.AnalogOutput',
        description = 'Syringe diameter for first pump',
        tangodevice = tango_base + 'refsans/syringe/pump0diameter',
    ),
    pump0_rate = device('nicos.devices.tango.AnalogOutput',
        description = 'Infusion rate for first pump',
        tangodevice = tango_base + 'refsans/syringe/pump0rate',
    ),
    pump0_run = device(code_base + 'PumpAnalogOutput',
        description = 'Move to volume to infuse (positive) or withdraw (negative)',
        tangodevice = tango_base + 'refsans/syringe/pump0infuse',
        precision = 0.0001,
    ),

    pump1_diameter = device('nicos.devices.tango.AnalogOutput',
        description = 'Syringe diameter for second pump',
        tangodevice = tango_base + 'refsans/syringe/pump1diameter',
    ),
    pump1_rate = device('nicos.devices.tango.AnalogOutput',
        description = 'Infusion rate for second pump',
        tangodevice = tango_base + 'refsans/syringe/pump1rate',
    ),
    pump1_run = device(code_base + 'PumpAnalogOutput',
        description = 'Move to volume to infuse (positive) or withdraw (negative)',
        tangodevice = tango_base + 'refsans/syringe/pump1infuse',
        precision = 0.0001,
    ),
)
