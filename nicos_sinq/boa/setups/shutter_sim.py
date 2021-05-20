description = 'This is shutter for use in simulations of BOA'

excludes = [
    'shutter',
]

sysconfig = {
    'datasinks': ['shuttersink',]
}

devices = dict(
    shutter = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Shutter',
        states = ['open', 'closed']
    ),
    shutterauto = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Flag if shutter is operated in automatic or manual mode',
        states = ['auto', 'manual']
    ),
    shuttersink = device('nicos_sinq.boa.devices.shuttersink.BoaShutterSink',
        description = 'Automatic shutter control',
        shutter1 = 'shutter',
        auto = 'shutterauto',
    ),
)
