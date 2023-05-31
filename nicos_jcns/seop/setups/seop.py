description = 'SECoP enabled 3He'

devices = dict(
    seop = device(
        'nicos.devices.secop.SecNodeDevice',
        description = 'main SEC node',
        uri = 'tcp://localhost:10767',
        prefix = '',
        auto_create = True,
        unit = '',
        visibility = set(),
    )
)

group = 'basic'

modules = ['nicos_jcns.seop.commands']

startupcode = '''
'''
