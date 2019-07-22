name = 'sinq_asciisink setup'

includes = ['stdsystem', 'scanning', 'detector']

sinklist = [
    'asciisink',
]

sysconfig = dict(datasinks = sinklist,)

devices = dict(
    asciisink = device('nicos_sinq.devices.sinqasciisink.SINQAsciiSink',
        description = "Sink for  SINQ ASCII writer",
        filenametemplate = [
            'test%(year)sn%(scancounter)06d.dat',
        ],
        templatefile = 'test/setups/custom/test_sinqascii.hdd',
        scaninfo = [('COUNTS','ctr1'), ('MONITOR1','mon1'), ('TIME','timer')],
    ),
)
