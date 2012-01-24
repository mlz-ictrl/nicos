description = 'Sample rotation motor'

includes = ['base']

devices = dict(
    srot   = device('nicos.taco.Motor',
                    tacodevice = 'mira/newportmc/motor',
                    )

)
