description = 'power supplies'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    temp_rack1 = device('nicos.devices.entangle.Sensor',
        description = 'PSU Temperature in Rack 1',
        tangodevice = tango_base + 'supply_temp/pow02',
        unit = 'degC',
    ),
    temp_rack2 = device('nicos.devices.entangle.Sensor',
        description = 'PSU Temperature in Rack 2',
        tangodevice = tango_base + 'supply_temp/pow23',
        unit = 'degC',
    ),
)

for i in range(1, 39):
    devices[f'pow{i:02d}'] = \
        device(
            'nicos_mlz.j_nse.devices.jnse.JNSEPowerSupply',
            description = f'Power Supply Port {i:02d}',
            tangodevice = tango_base + f'supply/pow{i:02d}',
            unit = 'A',
            precision = 0.002,
            visibility = ('metadata',) if i in [5, 9, 10, 11, 12] else \
                ('devlist', 'metadata', 'namespace'),
        )
