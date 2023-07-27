description = 'free channel at ana4gpio are used for humidity'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']


includes = ['ana4gpio01', 'ana4gpio02']
visibility = ('devlist', 'metadata', 'namespace')
Raspi_VDD = 3.3

devices = dict(
    humidity_po_rh = device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor rel humidity channel',
        device = '%s_ch3' % 'ana4gpio01',
        poly = [-12.5, 125 / Raspi_VDD],
        unit = 'percent',
        visibility = visibility,
    ),
    humidity_po_temp = device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor temperature channel',
        device = '%s_ch4' % 'ana4gpio01',
        poly = [-66.875, 218.75 / Raspi_VDD],
        unit = 'degC',
        visibility = visibility,
    ),
    humidity_yoke_rh = device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor rel humidity canel',
        device = '%s_ch2' % 'ana4gpio02',
        poly = [-12.5, 125 / Raspi_VDD],
        unit = 'percent',
        visibility = visibility,
    ),
    humidity_yoke_temp = device(code_base + 'analogencoder.AnalogEncoder',
        description = 'humidity sensor temperature channel',
        device = '%s_ch4' % 'ana4gpio02',
        poly = [-66.875, 218.75 / Raspi_VDD],
        unit = 'degC',
        visibility = visibility,
    ),
)
