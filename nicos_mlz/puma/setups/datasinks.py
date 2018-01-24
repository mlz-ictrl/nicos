description = 'Some additional data sinks'

group = 'lowlevel'

sysconfig = dict(
    datasinks = ['polsink',]
)

devices = dict(
    polsink = device('nicos_mlz.puma.devices.datasinks.PolarizationFileSink',
        description = 'writes the files for polarisation analysis',
        lowlevel = True,
    ),
)
