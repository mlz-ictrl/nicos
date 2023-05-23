description = 'Monitors the status of the Forwarder'

devices = dict(KafkaForwarder=device(
    'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
    description='Monitors the status of the Forwarder',
    statustopic='ymir_forwarder_status',
    brokers=['10.100.1.19:8093']), )
