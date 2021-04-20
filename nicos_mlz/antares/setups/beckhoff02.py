description = 'Beckhoff02 supported auxiliary devices'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/beckhoff02/beckhoff02_'

devices = {}

for i in range(1, 9):
    devices['beckhoff02_T%d' % i] = \
        device('nicos.devices.entangle.Sensor',
               description = 'Temperature Sensor %d' % i,
               tangodevice = tango_base + 't%d' % i,
               unit = 'degC',
              )
for i in range(1, 13):
    devices['beckhoff02_out%d' % i] = \
        device('nicos.devices.entangle.NamedDigitalOutput',
               description = 'Digital Output%d' % i,
               tangodevice = tango_base + 'out%d' % i,
               mapping = dict(On = 1, Off = 0),
               unit = '',
              )

