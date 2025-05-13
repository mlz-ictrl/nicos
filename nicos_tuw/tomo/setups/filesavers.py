description = 'Detector file savers'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['LiveViewSink', 'SingleRawImageSink']
)
#'SingleRawImageSink'

devices = dict(
    SingleRawImageSink = device('nicos.devices.datasinks.SingleRawImageSink',
    ),
    LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
    ),
)