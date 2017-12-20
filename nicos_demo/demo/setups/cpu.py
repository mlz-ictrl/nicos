description = 'cpu load device'
group = 'optional'

devices = dict(
    cpuload = device('nicos_demo.demo.devices.cpuload.CPULoad',
        description = 'CPU Load',
        interval = 1,
        fmtstr = '%.1f',
        unit = '%',
    ),
)
