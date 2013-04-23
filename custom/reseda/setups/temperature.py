description = 'NICOS startup setup'
group = 'lowlevel'

devices = dict(

    T   = device('devices.taco.TemperatureController',
                      tacodevice = '//resedasrv/reseda/ls336/control',
                      pollinterval = 0.7,
                      maxage = 5,
                      abslimits = (0, 300)),
    TA = device('devices.taco.TemperatureSensor',
                      tacodevice = '//resedasrv/reseda/ls336/sensa',
                      pollinterval = 0.7,
                      maxage = 5),
    TB = device('devices.taco.TemperatureSensor',
                      tacodevice = '//resedasrv/reseda/ls336/sensb',
                      pollinterval = 0.7,
                      maxage = 6),
    TC = device('devices.taco.TemperatureSensor',
                      tacodevice = '//resedasrv/reseda/ls336/sensc',
                      pollinterval = 0.7,
                      maxage = 6),
    TD = device('devices.taco.TemperatureSensor',
                      tacodevice = '//resedasrv/reseda/ls336/sensd',
                      pollinterval = 0.7,
                      maxage = 6),

)
