description = 'enable forwarding of detector image'

group = 'lowlevel'

datasinks = ['image_forwarder_sink']

devices = dict(
    image_forwarder_sink = device('nicos_sinq.devices.datasinks.sinq_datasinks.ImageForwarderSink',
        brokers = ['ess01.psi.ch:9092'],
        output_topic = 'SANS_detector',
    ),
)
