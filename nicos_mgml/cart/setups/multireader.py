description = 'Reading Keysight multimeter'

group = 'optional'

includes = ['busk34450']

devices = dict(
    MultiReader = device('nicos_mgml.devices.k34450.MultiReader',
        description = 'Keysight k23350 multimeter',
        fmtstr = '%.6f',
        k34450 = 'busk34450',
    ),
)
