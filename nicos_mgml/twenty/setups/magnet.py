description = 'Cryogenics SMS magnet controller'
group = 'lowlevel'

includes = ['alias_B', 'helium']

tango_base = 'tango://localhost:10000/20t/'

devices = dict(
    B_main = device('nicos.devices.entangle.RampActuator',
        description = 'Main switching power supply up to 18.5T',
        tangodevice = tango_base + 'sms/maincoil',
        pollinterval = 0.7,
        maxage = 2,
    ),
    magnet_mode = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Working mode of the main coils in 20T magnet',
        mapping = {'driven': 0, 'persistent': 1},
        tangodevice = tango_base + 'sms/mainmode',
        pollinterval = 5,
        maxage = 10,
    ),
    magnet_maincurrent = device('nicos.devices.entangle.AnalogInput',
        description = 'Current from the main PSU',
        tangodevice = tango_base + 'sms/maincurrent',
        pollinterval = 2,
        maxage = 5,
    ),
    magnet_mainvoltage = device('nicos.devices.entangle.AnalogInput',
        description = 'Voltage on the main PSU',
        tangodevice = tango_base + 'sms/mainvoltage',
        pollinterval = 2,
        maxage = 5,
    ),
    B_booster = device('nicos.devices.entangle.RampActuator',
        description = 'Secondary switching power supply up to 1.0T',
        tangodevice = tango_base + 'sms/sweepcoil',
        pollinterval = 0.7,
        maxage = 2,
    ),
    magnet_sweepcurrent = device('nicos.devices.entangle.AnalogInput',
        description = 'Current from the booster PSU',
        tangodevice = tango_base + 'sms/sweepcurrent',
        pollinterval = 2,
        maxage = 5,
    ),
    magnet_sweepvoltage = device('nicos.devices.entangle.AnalogInput',
        description = 'Voltage on the booster PSU',
        tangodevice = tango_base + 'sms/sweepvoltage',
        pollinterval = 2,
        maxage = 5,
    ),
    B_master = device('nicos_mgml.twenty.devices.sms_magnet.MasterMagnet',
        description = 'Overall field on sample',
        maindev = 'B_main',
        boosterdev = 'B_booster',
        pollinterval = 0.7,
        maxage = 5,
        abslimits = (-19.5,19.5),
    ),
)

alias_config = {
    'B': {'B_master': 100},
}
