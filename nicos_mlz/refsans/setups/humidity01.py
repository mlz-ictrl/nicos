description = 'Refsans 4 analog 1 GPIO on Raspberry'

group = 'plugplay'

instrument_values = configdata('instrument.values')
tango_base = 'tango://%s:10000/test/ads/' % setupname
code_base = instrument_values['code_base']
lowlevel = ()
visibility = ('devlist', 'metadata', 'namespace')
Raspi_VDD = 3.3

devices = dict(
    humidity_hutch1_rh = device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor rel humidity channel @ hutch',
        tangodevice = tango_base + 'ch1',
        unit = 'percent',
        fmtstr = '%.1f',
        visibility = visibility,
    ),
    humidity_hutch1_temp = device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor temperature channel @ hutch',
        tangodevice = tango_base + 'ch2',
        unit = 'degC',
        fmtstr = '%.1f',
        visibility = visibility,
    ),
    humidity_hutch2_rh = device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor rel humidity channel @ hutch',
        tangodevice = tango_base + 'ch3',
        unit = 'percent',
        fmtstr = '%.1f',
        visibility = visibility,
    ),
    humidity_hutch2_temp = device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor temperature channel @ hutch',
        tangodevice = tango_base + 'ch4',
        unit = 'degC',
        fmtstr = '%.1f',
        visibility = visibility,
    ),
)
