description = 'Vacuum readout devices using Leybold Center 3'

group = 'lowlevel'

tango_host = 'tango://refsanshw:10000/test/center/'

devices = dict(
    vacuum_CB = device('nicos.devices.tango.Sensor',
        description = 'Pressure in Chopper chamber',
        tangodevice = tango_host + 'center_0',
    ),
    vacuum_SFK = device('nicos.devices.tango.Sensor',
        description = 'Pressure in beam guide chamber',
        tangodevice = tango_host + 'center_1',
    ),
    vacuum_SR = device('nicos.devices.tango.Sensor',
        description = 'Pressure in scattering tube',
        tangodevice = tango_host + 'center_2',
    ),
)
