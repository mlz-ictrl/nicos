description = 'NICOS startup setup'
group = 'lowlevel'

devices = dict(

    C1   = device('devices.taco.DigitalOutput',
                      tacodevice = '//resedasrv/reseda/iotech_2/dev0',
                      pollinterval = 5,
                      maxage = 8),

    C2 = device('devices.taco.DigitalOutput',
                      tacodevice = '//resedasrv/reseda/iotech_2/dev1',
                      pollinterval = 5,
                      maxage = 8),

    C3 = device('devices.taco.DigitalOutput',
                       tacodevice = '//resedasrv/reseda/iotech_3/dev0',
                       pollinterval = 5,
                       maxage = 8),

    C4 = device('devices.taco.DigitalOutput',
                       tacodevice = '//resedasrv/reseda/iotech_3/dev1',
                       pollinterval = 5,
                       maxage = 8),

    C5 = device('devices.taco.DigitalOutput',
                       tacodevice = '//resedasrv/reseda/iotech_4/dev0',
                       pollinterval = 5,
                       maxage = 8),

    C6 = device('devices.taco.DigitalOutput',
                       tacodevice = '//resedasrv/reseda/iotech_4/dev1',
                       pollinterval = 5,
                       maxage = 8),

)
