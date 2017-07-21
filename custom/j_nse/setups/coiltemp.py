description = 'main coil temperatures'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    coil_p1 = device('nicos.devices.tango.Sensor',
                     description = 'vacuum in coil 1 vessel',
                     tangodevice = tango_base + 'coilpressure/p1',
                     unit = 'mbar',
                     fmtstr = '%.3g',
                     pollinterval = 60,
                     maxage = 130,
                    ),
    coil_p2 = device('nicos.devices.tango.Sensor',
                     description = 'vacuum in coil 2 vessel',
                     tangodevice = tango_base + 'coilpressure/p2',
                     unit = 'mbar',
                     fmtstr = '%.3g',
                     pollinterval = 60,
                     maxage = 130,
                    ),
)

sensor_names = {
#    (1, 1): 'xyz',
}

channels = ['', 'A', 'C1', 'C2', 'C3', 'C4', 'C5',
            'B', 'D1', 'D2', 'D3', 'D4', 'D5']

for n in range(1, 5):
    for i in range(1, 13):
        default_name = 'coil_t%d_%02d' % (n, i)
        devices[sensor_names.get((n, i), default_name)] = \
            device('nicos.devices.tango.Sensor',
                   description = 'LakeShore %d, channel %s' % (n, channels[i]),
                   tangodevice = tango_base + 'coiltemp/t%d_%d' % (n, i),
                   unit = 'K',
                   pollinterval = 60,
                   maxage = 130,
                  )
