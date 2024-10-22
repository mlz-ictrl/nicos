description = 'next bus departure'

group = 'lowlevel'

devices = dict(
    Bus = device('nicos_mgml.devices.bus.Bus',
        description = "Next departure of the bus from station 'Kuchyňka' "
                      'to the Nádraží Holešovice',
        fmtstr = '%s',
        destination = 'Nádraží Holešovice',
    ),
)
