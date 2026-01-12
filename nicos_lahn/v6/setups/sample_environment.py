description = 'Sample environment setup'

group = 'plugplay'
node = '9854'
devices = dict(
    sample_environment=device('nicos.devices.secop.SecNodeDevice',
                              uri='tcp://frappy:' + node,  # frappy: frappy's container IP
                              auto_create=True,
                              visibility=(),
                              ),
)
startupcode = '''
CreateConfigSecop()
'''
