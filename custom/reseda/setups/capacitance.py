description = 'RESEDA capacity box'

group = 'lowlevel'

nethost = 'resedasrv'

devices = dict(

    C00 = device('devices.taco.DigitalOutput',
                 description = 'K0',
                 tacodevice = '//%s/reseda/iotech_2/dev0' % (nethost,),
                 pollinterval = 5,
                 maxage = 8,
                ),

    C01 = device('devices.taco.DigitalOutput',
                 description = 'K0',
                 tacodevice = '//%s/reseda/iotech_2/dev1' % (nethost,),
                 pollinterval = 5,
                 maxage = 8,
                ),

    C10 = device('devices.taco.DigitalOutput',
                 description = 'K1',
                 tacodevice = '//%s/reseda/iotech_3/dev0' % (nethost,),
                 pollinterval = 5,
                 maxage = 8,
                ),

    C11 = device('devices.taco.DigitalOutput',
                 description = 'K1',
                 tacodevice = '//%s/reseda/iotech_3/dev1' % (nethost,),
                 pollinterval = 5,
                 maxage = 8,
                ),

    C20 = device('devices.taco.DigitalOutput',
                 description = 'K2',
                 tacodevice = '//%s/reseda/iotech_4/dev0' % (nethost,),
                 pollinterval = 5,
                 maxage = 8,
                ),

    C21 = device('devices.taco.DigitalOutput',
                 description = 'K2',
                 tacodevice = '//%s/reseda/iotech_4/dev1' % (nethost,),
                 pollinterval = 5,
                 maxage = 8,
                ),

)
