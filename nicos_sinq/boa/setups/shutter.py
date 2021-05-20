description = 'The BOA shutter'

excludes = [
    'shutter_sim',
]

sysconfig = {
    'datasinks': ['shuttersink',]
}

devices = dict(
    shutter = device('nicos_sinq.boa.devices.adamshutter.AdamShutter',
        description = 'ADAM shutter control module',
        host = 'boa-plc1',
        port = 502,
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
