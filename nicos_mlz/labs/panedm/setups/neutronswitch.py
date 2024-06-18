description = 'SECoP enabled Neutron trap'

group = 'basic'

host = '192.168.0.40'

devices = dict(
    nswitch = device(
        'nicos.devices.secop.SecNodeDevice',
        description = 'main SEC node',
        uri = f'tcp://{host}:10767',
        prefix = '',
        auto_create = True,
        unit = '',
        visibility = set(),
    )
)

startupcode = '''
'''
