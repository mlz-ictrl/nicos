description = 'Refsans 4 analog 1 GPIO on Raspberry'

group = 'plugplay'

instrument_values = configdata('instrument.values')
tango_base = 'tango://%s:10000/test/ads/' % setupname
code_base = instrument_values['code_base']
lowlevel = ()
visibility = ('devlist', 'metadata', 'namespace')
Raspi_VDD = 3.3

devices = {
    f'{setupname}_ch1': device('nicos.devices.entangle.Sensor',
        description = 'ADin0',
        tangodevice = tango_base + 'ch1',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    f'{setupname}_ch2': device('nicos.devices.entangle.Sensor',
        description = 'ADin1',
        tangodevice = tango_base + 'ch2',
        unit = 'V',
        fmtstr = '%.4f',
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
    'humidity_hutch1_rh' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor rel humidity channel @ hutch',
        device = f'{setupname}_ch1',
        poly = [-12.5, 125 / Raspi_VDD],
        unit = 'percent',
        visibility = visibility,
    ),
    'humidity_hutch1_temp' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor temperature channel @ hutch',
        device = f'{setupname}_ch2',
        poly = [-66.875, 218.75 / Raspi_VDD],
        unit = 'degC',
        visibility = visibility,
    ),
    'humidity_hutch2_rh' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor rel humidity channel @ hutch',
        device = f'{setupname}_ch3',
        poly = [-12.5, 125 / Raspi_VDD],
        unit = 'percent',
        visibility = visibility,
    ),
    'humidity_hutch2_temp' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor temperature channel @ hutch',
        device = f'{setupname}_ch4',
        poly = [-66.875, 218.75 / Raspi_VDD],
        unit = 'degC',
        visibility = visibility,
    ),
}
