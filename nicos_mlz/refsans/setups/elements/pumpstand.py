description = 'Pumpstand devices using Pluto'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'pumpstand/plc/'

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    pressure_CB = device('nicos.devices.entangle.Sensor',
        description = 'Pressure in CB (provided by Pumpstand)',
        tangodevice = tango_base + '_read_p_chopperburg',
    ),
    pressure_SFK = device('nicos.devices.entangle.Sensor',
        description = 'Pressure in CB (provided by Pumpstand)',
        tangodevice = tango_base + '_read_p_strahlfuehrungskammer',
    ),
    pressure_SR = device('nicos.devices.entangle.Sensor',
        description = 'Pressure in CB (provided by Pumpstand)',
        tangodevice = tango_base + '_read_p_streurohr',
    ),
    pump_CB = device('nicos.devices.generic.Switcher',
        description = 'Pumping state & control device for CB',
        moveable = device('nicos.devices.entangle.DigitalOutput',
            description = 'pump CB (provided by Pumpstand)',
            tangodevice = tango_base + '_ctrl_chopperburg',
        ),
        precision = 0.01,
        lowlevel = True,
        mapping = dict(vent = 1, off = 0, pump = -1),
    ),
    pump_SFK = device('nicos.devices.generic.Switcher',
        description = 'Pumping state & control device for SFK',
        moveable = device('nicos.devices.entangle.DigitalOutput',
            description = 'pump CB (provided by Pumpstand)',
            tangodevice = tango_base + '_ctrl_strahlfuehrungskammer',
        ),
        precision = 0.01,
        lowlevel = True,
        mapping = dict(vent = 1, off = 0, pump = -1),
    ),
    pump_SR = device('nicos.devices.generic.Switcher',
        description = 'Pumping state & control device for SR',
        moveable = device('nicos.devices.entangle.DigitalOutput',
            description = 'pump CB (provided by Pumpstand)',
            tangodevice = tango_base + '_ctrl_streurohr',
        ),
        precision = 0.01,
        lowlevel = True,
        mapping = dict(vent = 1, off = 0, pump = -1),
    ),
    pressuresetpoint3 = device('nicos.devices.entangle.Sensor',
        description = 'Pressure in CB (provided by Pumpstand)',
        tangodevice = tango_base + '_param_setpoint3',
        lowlevel = True,
    ),
    pressurefehlerbits = device('nicos.devices.entangle.Sensor',
        description = 'Pressure in CB (provided by Pumpstand)',
        tangodevice = tango_base + '_state_fehlerbits',
        lowlevel = True,
    ),
    pressureventile = device('nicos.devices.entangle.Sensor',
        description = 'Pressure in CB (provided by Pumpstand)',
        tangodevice = tango_base + '_state_pumpen_ventile',
        lowlevel = True,
    ),
)
