description = 'Refsans 4 analog 1 GPIO on Raspberry'

group = 'optional'

instrument_values = configdata('instrument.values')
tango_base = 'tango://%s:10000/test/ads/' % setupname
code_base = instrument_values['code_base']
lowlevel = ('devlist', 'metadata', 'namespace')
Raspi_VDD = 3.3

devices = {
    '%s_ch1' % setupname : device('nicos.devices.entangle.Sensor',
        description = 'ADin0',
        tangodevice = tango_base + 'ch1',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    '%s_ch2' % setupname : device('nicos.devices.entangle.Sensor',
        description = 'ADin1',
        tangodevice = tango_base + 'ch2',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    '%s_ch3' % setupname : device('nicos.devices.entangle.Sensor',
        description = 'ADin2',
        tangodevice = tango_base + 'ch3',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    '%s_ch4' % setupname : device('nicos.devices.entangle.Sensor',
        description = 'ADin3',
        tangodevice = tango_base + 'ch4',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    'humidity_Rack4_rh' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor rel humidity channel',
        device = '%s_ch2' % 'ana4gpio03',
        poly = [-12.5, 125/Raspi_VDD],
        unit = 'percent',
        visibility = lowlevel,
    ),
    'humidity_Rack4_temp' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor temperature channel',
        device = '%s_ch1' % 'ana4gpio03',
        poly = [-66.875, 218.75/Raspi_VDD],
        unit = 'Cdeg',
        visibility = lowlevel,
    ),
}
