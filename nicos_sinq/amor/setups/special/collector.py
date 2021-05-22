description = 'setup for the NICOS collector'
group = 'special'

devices = dict(
    CacheKafka = device('nicos_ess.devices.cache_kafka_forwarder.CacheKafkaForwarder',
        dev_ignore = ['space', 'sample'],
        brokers = ['ess01.psi.ch:9092'],
        output_topic = "AMOR_nicosForwarder",
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'localhost:14869',
        forwarders = ['CacheKafka'],
    ),
)
