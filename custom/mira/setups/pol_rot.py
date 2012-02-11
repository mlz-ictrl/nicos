description = 'Sample rotation motor'

includes = ['base']

devices = dict(
    polrot   = device('nicos.taco.Motor',
                    tacodevice = 'mira/motor/temp',
                    abslimits = (-180, 180),
                    )

)
