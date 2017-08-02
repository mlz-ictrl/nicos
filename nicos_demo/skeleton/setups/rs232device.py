description = 'Example setups for RS232 devices'

devices = dict(
    rs232 = device('nicos_demo.skeleton.devices.rs232device.RS232Example',
        description = 'Sample device using direct RS232 communication',
        port = '/dev/ttyS01',
        unit = 'unit',
    ),
)
