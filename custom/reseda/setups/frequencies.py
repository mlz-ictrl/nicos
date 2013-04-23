description = 'NICOS startup setup'
group = 'lowlevel'

devices = dict(

    F0 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/hp33250a_1/freq',
                     pollinterval = 5,
                     maxage = 8),

    F1 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/hp33250a_2/freq',
                     pollinterval = 5,
                     maxage = 8),

    F2 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/hp33250a_3/freq',
                     pollinterval = 5,
                     maxage = 8),

    Fu0 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/hp33250a_1/amp',
                     pollinterval = 5,
                     maxage = 8),

    Fu1 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/hp33250a_2/amp',
                     pollinterval = 5,
                     maxage = 8),

    Fu2 = device('devices.taco.AnalogInput',
                     tacodevice = '//resedasrv/reseda/hp33250a_3/amp',
                     pollinterval = 5,
                     maxage = 8),

    RF0 = device('reseda.frequencies.Frequencies',
                     tacodevice = '//resedasrv/reseda/nigpib/keithley0',
                     pollinterval = 5,
                     maxage = 8),

    RF1 = device('reseda.frequencies.Frequencies',
                     tacodevice = '//resedasrv/reseda/nigpib/keithley1',
                     pollinterval = 5,
                     maxage = 8),

    RF2 = device('reseda.frequencies.Frequencies',
                     tacodevice = '//resedasrv/reseda/nigpib/keithley2',
                     pollinterval = 5,
                     maxage = 8),

)
