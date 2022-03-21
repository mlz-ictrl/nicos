devices = dict(
    KafkaForwarder = device('nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description = 'Monitors and controls forward-epics-to-kafka',
        statustopic = 'TEST_forwarderStatus',
        brokers = [
            'localhost:9092',
        ],
    ),
)
