description = 'setup for the NICOS collector'
group = 'special'

KAFKA_BROKERS = ['10.102.80.32:8093']

devices = dict(
    CacheKafka=device(
        'nicos_ess.devices.cache_kafka_forwarder.CacheKafkaForwarder',
        dev_ignore=['space', 'sample'],
        brokers=KAFKA_BROKERS,
        output_topic='nido_nicos_devices',
    ),
    Collector=device(
        'nicos.services.collector.Collector',
        cache='localhost:14869',
        forwarders=['CacheKafka'],
    ),
)
