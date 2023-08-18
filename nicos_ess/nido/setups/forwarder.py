description = 'Monitors the status of the Forwarder'

KAFKA_BROKERS = ['10.102.80.32:8093']

devices = dict(
    KafkaForwarder=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description='Monitors the status of the Forwarder',
        statustopic='nido_forwarder_status',
        brokers=KAFKA_BROKERS,
    ),
)
