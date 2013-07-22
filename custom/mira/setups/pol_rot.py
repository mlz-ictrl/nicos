description = 'Sample rotation motor'

includes = ['base']

devices = dict(
    polrot   = device('devices.taco.Motor',
                    tacodevice = '//mirasrv/mira/motor/temp',
                    abslimits = (-180, 180),
                    )

)
