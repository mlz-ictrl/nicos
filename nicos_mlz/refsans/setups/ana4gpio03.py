description = 'Refsans 4 analog 3 GPIO on Raspberry'

group = 'optional'

instrument_values = configdata('instrument.values')
tango_base = f'tango://{setupname}:10000/test/ads/'
code_base = instrument_values['code_base']
lowlevel = ('devlist', 'metadata', 'namespace')

devices = {
    'humidity_Rack4_temp' : device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor temperature channel',
        tangodevice = tango_base + 'ch1',
        unit = 'degC',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    'humidity_Rack4_rh' : device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor rel humidity channel',
        tangodevice = tango_base + 'ch2',
        fmtstr = '%.4f',
        unit = 'percent',
        visibility = lowlevel,
    ),
    f'{setupname}_ch3': device('nicos.devices.entangle.Sensor',
        description = 'ADin2',
        tangodevice = tango_base + 'ch3',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    f'{setupname}_ch4': device('nicos.devices.entangle.Sensor',
        description = 'ADin3',
        tangodevice = tango_base + 'ch4',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
}
