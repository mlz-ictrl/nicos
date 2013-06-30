description = 'cpu load device'

group = 'lowlevel'

includes = []

devices = dict(
    cpuload = device('demo.cpuload.CPULoad',
                     description = 'CPU Load',
                     interval = 1,
                     fmtstr = '%.1f',
                     unit = '%',
                    ),
)
