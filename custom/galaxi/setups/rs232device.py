description = 'Example setups for RS232 devices'

nethost = 'galaxisrv'

devices = dict(
    rs232 = device('galaxi.rs232device.RS232Example',
                   description = 'Sample device using direct RS232 communication',
                   port = '/dev/ttyS01',
                   unit = 'unit',
                  ),
    rs232taco = device('galaxi.rs232device.RS232TACOExample',
                       description = 'Sample device using TACO RS232 communication',
                       tacodevice = '//%s/instr/network/rs232' % (nethost,),
                       unit = 'unit',
                      ),
)
