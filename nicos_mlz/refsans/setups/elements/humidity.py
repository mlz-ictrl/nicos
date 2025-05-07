description = 'humidity and temperatures'

group = 'lowlevel'

visibility = ('devlist', 'metadata', 'namespace')

devices = dict(
    humidity_po_rh = device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor rel humidity channel',
        tangodevice = 'tango://ana4gpio01:10000/test/ads/ch3',
        fmtstr = '%.4f',
        unit = 'percent',
        visibility = visibility,
    ),
    humidity_po_temp = device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor temperature channel',
        tangodevice = 'tango://ana4gpio01:10000/test/ads/ch4',
        fmtstr = '%.4f',
        unit = 'degC',
        visibility = visibility,
    ),
    humidity_yoke_rh = device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor rel humidity channel',
        tangodevice = 'tango://ana4gpio02:10000/test/ads/ch2',
        fmtstr = '%.4f',
        unit = 'percent',
        visibility = visibility,
    ),
    humidity_yoke_temp = device('nicos.devices.entangle.Sensor',
        description = 'humidity sensor temperature channel',
        tangodevice = 'tango://ana4gpio02:10000/test/ads/ch4',
        fmtstr = '%.4f',
        unit = 'degC',
        visibility = visibility,
    ),
)
