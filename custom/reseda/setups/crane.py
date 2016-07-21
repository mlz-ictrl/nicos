description = 'Setup for RESEDA temperature measuring devices'

group = 'lowlevel'

nethost = 'resedasrv'

devices = dict(
    Crane = device('devices.taco.AnalogInput',
        description = 'Position of Crane SMC10',
        tacodevice = '//tacodb.taco.frm2/frm2/smc10/pos',
        pollinterval = 5,
        maxage = 10,
    ),
)
