description = 'main coil cooling compressors'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict()

for n in range(1, 5):
    devices['compressor_%d' % n] = \
            device('nicos.devices.tango.NamedDigitalInput',
                   description = 'Compressor state',
                   tangodevice = tango_base + 'compressor/onoff%d' % n,
                   mapping = {'on': 1, 'off': 0},
                   pollinterval = 60,
                   maxage = 130,
                  )
    devices['he_temp_%d' % n] = \
            device('nicos.devices.tango.Sensor',
                   description = 'Compressor He temp',
                   tangodevice = tango_base + 'compressor/heliumtemp%d' % n,
                   fmtstr = '%.1f',
                   unit = 'degC',
                   pollinterval = 60,
                   maxage = 130,
                  )
    devices['oil_temp_%d' % n] = \
            device('nicos.devices.tango.Sensor',
                   description = 'Compressor oil temp',
                   tangodevice = tango_base + 'compressor/oiltemp%d' % n,
                   fmtstr = '%.1f',
                   unit = 'degC',
                   pollinterval = 60,
                   maxage = 130,
                  )
    devices['water_temp_in_%d' % n] = \
            device('nicos.devices.tango.Sensor',
                   description = 'Compressor water inlet temp',
                   tangodevice = tango_base + 'compressor/waterintemp%d' % n,
                   fmtstr = '%.1f',
                   unit = 'degC',
                   pollinterval = 60,
                   maxage = 130,
                  )
    devices['water_temp_out_%d' % n] = \
            device('nicos.devices.tango.Sensor',
                   description = 'Compressor water outlet temp',
                   tangodevice = tango_base + 'compressor/waterouttemp%d' % n,
                   fmtstr = '%.1f',
                   unit = 'degC',
                   pollinterval = 60,
                   maxage = 130,
                  )
    devices['he_pressure_%d' % n] = \
            device('nicos.devices.tango.Sensor',
                   description = 'Compressor high-side Helium pressure',
                   tangodevice = tango_base + 'compressor/pressurehigh%d' % n,
                   fmtstr = '%.1f',
                   unit = 'psi',
                   pollinterval = 60,
                   maxage = 130,
                  )
