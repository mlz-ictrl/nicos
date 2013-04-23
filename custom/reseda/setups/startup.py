description = 'NICOS startup setup'
group = 'lowlevel'

includes = ['powersupply', 'temperature', 'capacitance','attenuatorsSlits']

devices = dict(

    m1 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/husco1/motor7',
                     pollinterval = 5,
                     maxage = 8),

    m2 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/husco1/motor8',
                     pollinterval = 5,
                     maxage = 8),

    m3 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/husco1/motor1',
                     pollinterval = 5,
                     maxage = 8),

    m4 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/husco1/motor2',
                     pollinterval = 5,
                     maxage = 8),

    m5 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/husco1/motor3',
                     pollinterval = 5,
                     maxage = 8),

    m6 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/husco1/motor4',
                     pollinterval = 5,
                     maxage = 8),

    m7 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/husco1/motor5',
                     pollinterval = 5,
                     maxage = 8),


    Sel = device('reseda.selector.Selector',
                     tacodevice = '//resedasrv/reseda/rs232/sel',
                     pollinterval = 300,
                     maxage = 600),

    Lambda = device('reseda.selector.Wavelength',
                     selector = 'Sel',
                     pollinterval = 32,
                     maxage = 61),

    Q1 = device('reseda.scatteringVector.ScatteringVector',
                     wavelength = 'Lambda',
                     twotheta = 'm1',
                     pollinterval = 32,
                     maxage = 61),

    Q2 = device('reseda.scatteringVector.ScatteringVector',
                     wavelength = 'Lambda',
                     twotheta = 'm2',
                     pollinterval = 32,
                     maxage = 61),

)
