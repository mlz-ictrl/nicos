description = 'Cryomagnetics 4G magnet controller'
group = 'lowlevel'

includes = ['alias_B', 'drpanel']

tango_base = 'tango://localhost:10000/dr/'

devices = dict(
    B_main9t = device('nicos.devices.entangle.RampActuator',
        description = 'Main switching power supply up to 9T',
        tangodevice = tango_base + 'ps4g/coil',
        pollinterval = 0.7,
        maxage = 2,
    ),

    magnet_mode9t = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Working mode of the main coils in 9T magnet',
        mapping = {'driven': 0, 'persistent': 1},
        tangodevice = tango_base + 'ps4g/mode',
        pollinterval = 5,
        maxage = 10,
    ),

    magnet_current9t = device('nicos.devices.entangle.AnalogInput',
        description = 'Current from the main PSU',
        tangodevice = tango_base + 'ps4g/current',
        pollinterval = 2,
        maxage = 5,
    ),
    magnet_voltage9t = device('nicos.devices.entangle.AnalogInput',
        description = 'Voltage on the main PSU',
        tangodevice = tango_base + 'ps4g/voltage',
        pollinterval = 2,
        maxage = 5,
    ),
)

alias_config = {
    'B': {'B_main9t': 100},
}
