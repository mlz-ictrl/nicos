description = 'The Knauer Azura valve.'

devices = dict(
    KV=device(
        'nicos_ess.loki.devices.knauer_valve.KnauerValve',
        description='.',
        pvroot='SE-SEE:SE-KVU-001:',
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    ),
)
