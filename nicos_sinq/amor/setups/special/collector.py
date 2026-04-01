description = 'setup for the NICOS collector'
group = 'special'

devices = dict(
    CacheKafka = device('nicos_sinq.devices.cache_kafka_forwarder.CacheKafkaForwarder',
        dev_ignore = ['space', 'sample', 'controller_slm'],
        brokers = configdata('config.KAFKA_BROKERS'),
        output_topic = configdata('config.NICOS_FORWARDER_TOPIC'),
    ),
    Collector = device('nicos.services.collector.Collector',
        cache = 'localhost:14869',
        forwarders = ['CacheKafka'],
    ),
)
