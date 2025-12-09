# TODO I think this file can be removed, so I am hiding it from the list to see
# if anyone complains
group = 'lowlevel'


description = 'This is shutter for use in simulations of BOA'

excludes = [
    'shutter',
]

sysconfig = {'datasinks': ['shuttersink',]}

devices = dict(
    shutter = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Shutter',
        states = ['open', 'close', 'closed']
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
