description = 'setup for ASCII file writing'

sysconfig = dict(datasinks = ['sinqsink'])

excludes = ['nexus']

devices = dict(
    sinqsink = device('nicos_sinq.devices.sinqasciisink.SINQAsciiSink',
        filenametemplate = ['focus%(year)sn%(scancounter)06d.dat'],
        templatefile = 'nicos_sinq/focus/focus.hdd',
        scaninfo = [
            ('COUNTS', 'monitor1'), ('PROTOCOUNT', 'protoncount'),
            ('TIME', 'elapsedtime')
        ],
    ),
)
