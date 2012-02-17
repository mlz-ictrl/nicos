description = 'Sample stick rotation motor'
group = 'optional'

includes = ['base']

devices = dict(
    srot   = device('nicos.taco.Motor',
                    tacodevice = 'mira/newportmc/motor',
                    )

)
