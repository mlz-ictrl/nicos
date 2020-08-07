description = 'Polarized neutron beam measurements'

group = 'basic'

includes = [
    'pumabase', 'seccoll', 'collimation', 'ios', 'hv', 'notifiers', 'multidet',
    'multiana', 'rdcad', 'opticalbench', 'detector', 'ana_alias', 'pollengths',
    'slits',
]

tango_base = 'tango://mesydaq.puma.frm2.tum.de:10000/qm/qmesydaq/'

devices = dict(
    channels = device('nicos.devices.vendor.qmesydaq.tango.MultiCounter',
        tangodevice = tango_base + 'image',
        lowlevel = True,
        channels = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Puma detector QMesydaq device (11 counters)',
        timers = ['timer'],
        monitors = ['mon1'],
        counters = ['channels'],
        images = [],
        maxage = 86400,
        pollinterval = None,
    ),
)

startupcode = '''
med.opmode = 'pa'
SetDetectors(det)
set('image', 'listmode', False)
'''
