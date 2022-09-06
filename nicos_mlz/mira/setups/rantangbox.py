description = 'SECoP enabled flexbox/rantangbox'

group = 'plugplay'

# note: box is actually named flexbox now, but DNS entry is still rantangbox
devices = dict(
    flexbox_secnode = device('nicos.devices.secop.SecNodeDevice',
    description='main SEC node',
    prefix = 'flexbox',
    uri = 'tcp://rantangbox.mira.frm2.tum.de:10767',
    auto_create = True,
    unit='',
    visibility=set(),
    )
)

startupcode = '''
'''
