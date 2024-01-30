description = 'Setup for New Era Syringe pumps'

group = 'plugplay'

tango_base = 'tango://syring01.refsans.frm2.tum.de:10000/box/syringe/'

devices = dict(
    pump0_diameter = device('nicos.devices.entangle.AnalogOutput',
        description = 'Syringe diameter for first pump',
        tangodevice = tango_base + 'pump0diameter',
    ),
    pump0_rate = device('nicos.devices.entangle.AnalogOutput',
        description = 'Infusion rate for first pump',
        tangodevice = tango_base + 'pump0rate',
    ),
    pump0_run = device('nicos_mlz.refsans.devices.syringepump.PumpAnalogOutput',
        description = 'Move to volume to infuse (positive) or withdraw (negative)',
        tangodevice = tango_base + 'pump0infuse',
        precision = 0.0001,
    ),
    pump1_diameter = device('nicos.devices.entangle.AnalogOutput',
        description = 'Syringe diameter for second pump',
        tangodevice = tango_base + 'pump1diameter',
    ),
    pump1_rate = device('nicos.devices.entangle.AnalogOutput',
        description = 'Infusion rate for second pump',
        tangodevice = tango_base + 'pump1rate',
    ),
    pump1_run = device('nicos_mlz.refsans.devices.syringepump.PumpAnalogOutput',
        description = 'Move to volume to infuse (positive) or withdraw (negative)',
        tangodevice = tango_base + 'pump1infuse',
        precision = 0.0001,
    ),
)
