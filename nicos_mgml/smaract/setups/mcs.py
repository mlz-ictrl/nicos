description = 'MCS nanomanipulator'

group = 'basic'

devices = dict(
    secnode = device('nicos.devices.secop.SecNodeDevice',
        description='MCS secnode',
        uri='localhost:10767',
        auto_create=True,
        prefix='',
        # count=0,
        # pollinterval=1,
    ),
)