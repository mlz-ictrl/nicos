description = 'Monitors the status of the Forwarder'

devices = dict(
    KafkaForwarder=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description='Monitors the status of the Forwarder',
        statustopic='UTGARD_forwarderStatus',
        brokers=['172.30.242.20:9092']),
    )
