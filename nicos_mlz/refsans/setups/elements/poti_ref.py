description = 'reference values for the encoder potiometers'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']

devices = dict(
    wegbox_A_1ref = device('nicos.devices.tango.Sensor',
        description = 'wegbox_A_1ref',
        tangodevice = tango_base + 'test/WB_A/1_6',
    ),
    wegbox_A_2ref = device('nicos.devices.tango.Sensor',
        description = 'wegbox_A_2ref',
        tangodevice = tango_base + 'test/WB_A/2_6',
    ),
    wegbox_B_1ref = device('nicos.devices.tango.Sensor',
        description = 'wegbox_B_1ref',
        tangodevice = tango_base + 'test/WB_B/1_6',
    ),
    wegbox_B_2ref = device('nicos.devices.tango.Sensor',
        description = 'wegbox_B_2ref',
        tangodevice = tango_base + 'test/WB_B/2_6',
    ),
    wegbox_C_1ref = device('nicos.devices.tango.Sensor',
        description = 'wegbox_C_1ref',
        tangodevice = tango_base + 'test/WB_C/1_6',
    ),
    wegbox_C_2ref = device('nicos.devices.tango.Sensor',
        description = 'wegbox_C_2ref',
        tangodevice = tango_base + 'test/WB_C/2_6',
    ),
)
