description = 'Example setups for RS232 devices'

devices = dict(

    rs232     = device('skeleton.rs232device.RS232Example',
                       description='Sample device using direct RS232 communication',
                       port='/dev/ttyS01',
                       unit='unit',
                      ),
    rs232taco = device('skeleton.rs232device.RS232TACOExample',
                       description='Sample device using TACO RS232 communication',
                       tacodevice='//instrhost/instr/network/rs232',
                       unit='unit',
                      ),
)
