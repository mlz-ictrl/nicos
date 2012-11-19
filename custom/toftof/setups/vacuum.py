description = 'chopper vacuum readout'
includes = ['system']

nethost = 'toftofsrv'

devices = dict(
    vacbus = device('devices.vendor.toni.ModBus',
                    tacodevice = '//%s/toftof/rs232/ifvacuumcontrol' % (nethost,) ,
                    lowlevel = True),
    vac0   = device('devices.vendor.toni.Vacuum',
                    bus = 'vacbus',
                    addr = 0xF0,
                    channel = 0,
                    pollinterval = 10,
                    maxage = 12,
                    unit = 'mbar'),
    vac1   = device('devices.vendor.toni.Vacuum',
                    bus = 'vacbus',
                    addr = 0xF0,
                    channel = 1,
                    pollinterval = 10,
                    maxage = 12),
    vac2   = device('devices.vendor.toni.Vacuum',
                    bus = 'vacbus',
                    addr = 0xF0,
                    channel = 2,
                    pollinterval = 10,
                    maxage = 12),
    vac3   = device('devices.vendor.toni.Vacuum',
                    bus = 'vacbus',
                    addr = 0xF0,
                    channel = 3,
                    pollinterval = 10,
                    maxage = 12),
)
