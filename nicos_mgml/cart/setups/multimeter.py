description = 'Reading Keysight multimeter'

group = 'optional'

includes = ['busk34450']

devices = dict(
    Multimeter = device('nicos_mgml.devices.k34450.Multimeter',
        description = 'Keysight k23350 multimeter',
        fmtstr = '%.6f',
        k34450 = 'busk34450',
    ),
)
