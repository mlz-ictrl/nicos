description = 'Detector file savers'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['FITSImageSink']
)

devices = dict(
    FITSImageSink = device('nicos.devices.datasinks.FITSImageSink',
    ),
)
