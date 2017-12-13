description = 'Perform shape of sample scanning'

group = 'basic'

includes = ['sampletable', 'sick', 'system']

sysconfig = dict(
    datasinks = ['contoursink'],
)

devices = dict(
    contoursink = device('nicos.devices.datasinks.AsciiScanfileSink',
        lowlevel = True,
        filenametemplate = ['contour%(scancounter)08d.txt'],
    ),
)
