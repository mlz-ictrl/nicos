description = 'RESEDA attenuators'

group = 'lowlevel'

nethost = 'resedasrv'

devices = dict(

    # Att0   = device('devices.taco.DigitalOutput',
    #                 description = 'Attenuator 0',
    #                 tacodevice = '//%s/reseda/ics4861a/dout1' % (nethost,),
    #                 pollinterval = 5,
    #                 maxage = 8,
    #                ),
    #
    # Att1   = device('devices.taco.DigitalOutput',
    #                 description = 'Attenuator 1',
    #                 tacodevice = '//%s/reseda/ics4861a/dout2' % (nethost,),
    #                 pollinterval = 5,
    #                 maxage = 8,
    #                ),
    #
    # Att2   = device('devices.taco.DigitalOutput',
    #                 description = 'Attenuator 2',
    #                 tacodevice = '//%s/reseda/ics4861a/dout3' % (nethost,),
    #                 pollinterval = 5,
    #                 maxage = 8,
    #                ),
    Slit0 = device('devices.taco.DigitalOutput',
        description = 'Slit',
        tacodevice = '//%s/reseda/pci2032/dev0' % (nethost,),
        pollinterval = 10,
        maxage = 20,
    ),
)
