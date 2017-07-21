description = 'power supplies'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    temp_rack1 = device('nicos.devices.tango.Sensor',
                        description = 'PSU Temperature in Rack 1',
                        tangodevice = tango_base + 'JCNSPowerSupply/pow2_temp',
                        unit = 'degC',
                       ),
    temp_rack2 = device('nicos.devices.tango.Sensor',
                        description = 'PSU Temperature in Rack 2',
                        tangodevice = tango_base + 'JCNSPowerSupply/pow23_temp',
                        unit = 'degC',
                       ),
)

for i in range(1, 39):
    name = 'pow%d' % i
    devices[name] = \
        device('nicos.devices.tango.PowerSupply',
               description = 'Power Supply Port %d' % i,
               tangodevice = tango_base + 'JCNSPowerSupply/' + name,
               unit = 'A',
              )
