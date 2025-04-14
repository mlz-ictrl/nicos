description = 'Refsans 4 analog 1 GPIO on Raspberry'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = 'tango://%s:10000/test/ads/' % setupname
code_base = instrument_values['code_base']
#tango_base = f'tango://{setupname}:10000/test/ads/'
lowlevel = ()
visibility = {}

devices = {
    f'{setupname}_ch11': device('nicos.devices.entangle.Sensor',
        description = 'Modul 1 ADin0',
        tangodevice = tango_base + 'ch1',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    f'{setupname}_ch12': device('nicos.devices.entangle.Sensor',
        description = 'Modul 1 ADin1',
        tangodevice = tango_base + 'ch2',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    f'{setupname}_ch13': device('nicos.devices.entangle.Sensor',
        description = 'Modul 1 ADin2',
        tangodevice = tango_base + 'ch3',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    f'{setupname}_ch14': device('nicos.devices.entangle.Sensor',
        description = 'Modul 1 ADin3',
        tangodevice = tango_base + 'ch4',
        unit = 'V',
        fmtstr = '%.4f',
        visibility = lowlevel,
    ),
    'nok6r_analog' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'raspi weg for nok6r_motor',
        device = 'weg02_ch11',
        poly = [ 133.24031006011, -79.04824775868207 ], #2025-02-26 22:04:43 [133.709993, -79.051028], #2025-02-10 [134.160129, -79.404478],
        unit = 'mm',
        visibility = visibility,
    ),
    'nok6s_analog' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'raspi weg for nok6s_motor',
        device = 'weg02_ch12',
        poly = [ 146.46319570708954, -79.43279499114907 ], #2025-02-26 22:05:07 [147.061611, -79.469221], #2025-02-10 [147.649952, -79.999983],
        unit = 'mm',
        visibility = visibility,
    ),
    'zb2_analog' : device(code_base + 'analogencoder.AnalogEncoder',
        description = 'raspi weg for zb2_motor',
        device = 'weg02_ch13',
        poly = [ 143.78801687082745,     -158.6599965974629 ], #2025-02-26 22:05:25 [144.874950, -157.128477], #2025-02-10 [146.346574, -160.000041],
        unit = 'mm',
        visibility = visibility,
    ),
}
