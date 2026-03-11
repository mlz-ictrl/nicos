description = 'main coil cooling compressors'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict()

for n in range(1, 5):
    devices[f'compressor{n}'] = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'Compressor state',
        tangodevice = tango_base + f'compressor/onoff{n}',
        mapping = {'on': 1, 'off': 0},
        pollinterval = 60,
        maxage = 130,
    )
    devices[f'he_temp_{n}'] = device('nicos.devices.entangle.Sensor',
        description = 'Compressor He temp',
        tangodevice = tango_base + f'compressor/heliumtemp{n}',
        fmtstr = '%.1f',
        unit = 'degC',
        pollinterval = 60,
        maxage = 130,
    )
    devices[f'oil_temp_{n}'] = device('nicos.devices.entangle.Sensor',
        description = 'Compressor oil temp',
        tangodevice = tango_base + f'compressor/oiltemp{n}',
        fmtstr = '%.1f',
        unit = 'degC',
        pollinterval = 60,
        maxage = 130,
    )
    devices[f'water_temp_in_{n}'] = device('nicos.devices.entangle.Sensor',
        description = 'Compressor water inlet temp',
        tangodevice = tango_base + f'compressor/waterintemp{n}',
        fmtstr = '%.1f',
        unit = 'degC',
        pollinterval = 60,
        maxage = 130,
    )
    devices[f'water_temp_out_{n}'] = device('nicos.devices.entangle.Sensor',
        description = 'Compressor water outlet temp',
        tangodevice = tango_base + f'compressor/waterouttemp{n}',
        fmtstr = '%.1f',
        unit = 'degC',
        pollinterval = 60,
        maxage = 130,
    )
    devices[f'he_pressure_{n}'] = device('nicos.devices.entangle.Sensor',
        description = 'Compressor high-side Helium pressure',
        tangodevice = tango_base + f'compressor/pressurehigh{n}',
        fmtstr = '%.1f',
        unit = 'psi',
        pollinterval = 60,
        maxage = 130,
    )
