description = 'efu monitor'
group = 'optional'

devices = dict(
    efu = device('nicos_sinq.devices.efu_monitor.EFUStatistics',
        description = 'efu stats',
        port=2911
    ),
)
