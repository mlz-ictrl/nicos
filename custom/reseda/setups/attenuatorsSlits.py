description = 'NICOS startup setup'
group = 'lowlevel'

devices = dict(

    Att0   = device('devices.taco.DigitalOutput',
                      tacodevice = '//resedasrv/reseda/ics4861a/dout1',
                      pollinterval = 5,
                      maxage = 8),

    Att1   = device('devices.taco.DigitalOutput',
                      tacodevice = '//resedasrv/reseda/ics4861a/dout2',
                      pollinterval = 5,
                      maxage = 8),

    Att2   = device('devices.taco.DigitalOutput',
                      tacodevice = '//resedasrv/reseda/ics4861a/dout3',
                      pollinterval = 5,
                      maxage = 8),

)
