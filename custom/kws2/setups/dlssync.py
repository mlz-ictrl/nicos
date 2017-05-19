description = 'Synchronization with DLS measurement'

group = 'optional'

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    DLS = device('kws2.dlssync.DLSSync',
                 description = 'Synchronization with DLS measurement',
                 tangodevice = tango_base + 'dlssync/io',
                ),
)

startupcode = '''
AddDetector(DLS)
'''
