description = 'Vacuum readout devices using Leybold Center 3'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test/center' % nethost

devices = dict(
    vacuum_CB = device('devices.taco.AnalogInput',
                description = 'Pressure in Chopper chamber',
                tacodevice = '%s/center_0' % tacodev,
               ),
    vacuum_SFK = device('devices.taco.AnalogInput',
                 description = 'Pressure in beam guide chamber',
                 tacodevice = '%s/center_1' % tacodev,
                ),
    vacuum_SR = device('devices.taco.AnalogInput',
                description = 'Pressure in scattering tube',
                tacodevice = '%s/center_2' % tacodev,
               ),
)
