description = 'chopper vacuum readout'

group = 'lowlevel'

includes = ['system']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
#   vacbus = device('devices.vendor.toni.ModBus',
#                   tacodevice = '//%s/toftof/rs232/ifvacuumcontrol' % (nethost,) ,
#                   lowlevel = True,
#                  ),

#   vac0   = device('devices.vendor.toni.Vacuum',
#                   bus = 'vacbus',
#                   addr = 0xF0,
#                   channel = 0,
    vac0   = device('devices.taco.io.AnalogInput',
                    tacodevice = '//%s/toftof/vacuum/sens1' % (nethost, ),
                    pollinterval = 10,
                    maxage = 12,
                    unit = 'mbar',
                   ),
#   vac1   = device('devices.vendor.toni.Vacuum',
#                   bus = 'vacbus',
#                   addr = 0xF0,
#                   channel = 1,
    vac1   = device('devices.taco.io.AnalogInput',
                    tacodevice = '//%s/toftof/vacuum/sens2' % (nethost, ),
                    pollinterval = 10,
                    maxage = 12,
                   ),
#   vac2   = device('devices.vendor.toni.Vacuum',
#                   bus = 'vacbus',
#                   addr = 0xF0,
#                   channel = 2,
    vac2   = device('devices.taco.io.AnalogInput',
                    tacodevice = '//%s/toftof/vacuum/sens3' % (nethost, ),
                    pollinterval = 10,
                    maxage = 12,
                   ),
#   vac3   = device('devices.vendor.toni.Vacuum',
#                   bus = 'vacbus',
#                   addr = 0xF0,
#                   channel = 3,
    vac3   = device('devices.taco.io.AnalogInput',
                    tacodevice = '//%s/toftof/vacuum/sens4' % (nethost, ),
                    pollinterval = 10,
                    maxage = 12,
                   ),
)
