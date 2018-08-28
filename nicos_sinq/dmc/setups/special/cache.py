description = 'setup for the cache server'
group = 'special'

devices = dict(
    serializer=device(
        'nicos.services.cache.entry.serializer.flatbuffers.FlatbuffersCacheEntrySerializer'),

    DB=device(
        'nicos.services.cache.database.kafka.KafkaCacheDatabaseWithHistory',
        currenttopic='DMC_nicosCacheCompacted',
        historytopic='DMC_nicosCacheHistory',
        brokers=configdata('config.KAFKA_BROKERS'),
        loglevel='info',
        serializer='serializer'
    ),

    Server=device('nicos.services.cache.server.CacheServer',
                  db='DB',
                  server='',
                  loglevel='info',
                  ),
)
