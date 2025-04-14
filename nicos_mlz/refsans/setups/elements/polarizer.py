description = 'polarizer: master device and subelements'

group = 'optional'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']
lowlevel = {'metadata', 'devlist', 'namespace'}

excludes = ['flipper']


devices = {
    'flipper_guide_temp': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of Flipping Guide',
        tangodevice = tango_base + 'test/flipper/guide_temp',
        visibility = lowlevel,
    ),
    'flipper_coil_temp': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of Flipping Coil',
        tangodevice = tango_base + 'test/flipper/coil_temp',
        visibility = lowlevel,
    ),
    'flipper_current': device('nicos.devices.entangle.WindowTimeoutAO',
        description = 'Current of Flipping Coil',
        tangodevice = tango_base + 'test/flipper/current',
        precision = 0.1,
        visibility = lowlevel,
    ),
    'flipper_frequency': device('nicos.devices.entangle.AnalogInput',
        description = 'Frequency of Flipping Field',
        tangodevice = tango_base + 'test/flipper/frequency',
        visibility = lowlevel,
    ),
    'flipper': device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Flipper',
        tangodevice = tango_base + 'test/flipper/flipper',
        mapping = dict(ON = 1, OFF = 0),
    ),
    'polarizer_layer': device('nicos.devices.generic.ManualSwitch',
        description = 'adiabatic at b3',
        states = ['sagital', 'lateral', 'normal'],
    ),
    'guidefield_sfk': device('nicos.devices.entangle.PowerSupply',
        description = 'powersupply for guidefield_sfk',
        tangodevice = tango_base + 'refsans/ea01/ps',
        abslimits = (0, 20),
        visibility = lowlevel,
    ),
    'guidefield_po': device('nicos.devices.entangle.PowerSupply',
        description = 'powersupply for guidefield_sfk',
        tangodevice = tango_base + 'refsans/ea02/ps',
        abslimits = (0, 20),
        visibility = lowlevel,
    ),
}
