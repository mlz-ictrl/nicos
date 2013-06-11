description = 'NICOS startup setup'

group = 'lowlevel'

includes = ['powersupply', 'temperature', 'capacitance',
            'attenuatorsSlits', 'frequencies',
           ]

nethost = 'resedasrv'

devices = dict(

    m3 = device('devices.taco.AnalogInput',
                description = 'Motor - Ty',
                tacodevice = '//%s/reseda/husco1/motor1' % (nethost,),
                pollinterval = 5,
                maxage = 8,
               ),

    m4 = device('devices.taco.AnalogInput',
                description = 'Motor - Tx',
                tacodevice = '//%s/reseda/husco1/motor2' % (nethost,),
                pollinterval = 5,
                maxage = 8,
               ),

    m5 = device('devices.taco.AnalogInput',
                description = 'Motor - gl',
                tacodevice = '//%s/reseda/husco1/motor3' % (nethost,),
                pollinterval = 5,
                maxage = 8,
               ),

    m6 = device('devices.taco.AnalogInput',
                description = 'Motor - gu',
                tacodevice = '//%s/reseda/husco1/motor4' % (nethost,),
                pollinterval = 5,
                maxage = 8,
               ),

    m7 = device('devices.taco.AnalogInput',
                description = 'Omega',
                tacodevice = '//%s/reseda/husco1/motor5' % (nethost,),
                pollinterval = 5,
                maxage = 8,
               ),

)
