description = 'Perform shape of sample scanning'

group = 'basic'

includes = [
    'standard',
    'sampletable',
    'sick',
]

sysconfig = dict(
    datasinks = ['contoursink'],
)

devices = dict(
    contoursink = device('nicos.devices.datasinks.AsciiScanfileSink',
        filenametemplate = ['contour%(scancounter)08d.txt'],
    ),
)
