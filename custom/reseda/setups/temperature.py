description = 'Setup for RESEDA temperature measuring devices'

group = 'lowlevel'

nethost = 'resedasrv'

devices = dict(

    T  = device('devices.taco.TemperatureController',
                description = 'Controller',
                tacodevice = '//%s/reseda/ls336/control' % (nethost,),
                pollinterval = 0.7,
                maxage = 5,
                abslimits = (0, 300),
               ),

    TA = device('devices.taco.TemperatureSensor',
                description = 'Sensor A',
                tacodevice = '//%s/reseda/ls336/sensa' % (nethost,),
                pollinterval = 0.7,
                maxage = 5,
               ),

    TB = device('devices.taco.TemperatureSensor',
                description = 'Sensor B',
                tacodevice = '//%s/reseda/ls336/sensb' % (nethost,),
                pollinterval = 0.7,
                maxage = 6,
               ),

    TC = device('devices.taco.TemperatureSensor',
                description = 'Sensor C',
                tacodevice = '//%s/reseda/ls336/sensc' % (nethost,),
                pollinterval = 0.7,
                maxage = 6,
               ),

    TD = device('devices.taco.TemperatureSensor',
                description = 'Sensor D',
                tacodevice = '//%s/reseda/ls336/sensd' % (nethost,),
                pollinterval = 0.7,
                maxage = 6,
               ),

)
