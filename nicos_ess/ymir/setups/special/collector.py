description = 'setup for the NICOS collector'
group = 'special'

devices = dict(
    CacheKafka=device(
        'nicos_ess.devices.cache_kafka_forwarder.CacheKafkaForwarder',
        dev_ignore=['space', 'sample'],
        brokers=['localhost:9092'],
        output_topic="from_nicos",
    ),
    Collector=device('nicos.services.collector.Collector',
        cache='localhost:14869',
        forwarders=['CacheKafka'],
    ),
)
