description = 'Auxiliary temperature sensors'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/beckhoff02/beckhoff02_'

devices = {}

for i in range(1,9):
    devices['Temperature_Sensor_T%d' % i] = \
        device('nicos.devices.tango.Sensor',
               description = 'Temperature Sensor T%d' % i,
               tangodevice = tango_base + 't%d' % i,
               unit = 'degC',
              )

