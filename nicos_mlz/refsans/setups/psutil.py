description = 'PID setup'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

code_base = instrument_values['code_base']

devices = dict(
    cache = device(code_base + 'psutil.ProcessIdentifier',
        description = 'CPU utilization',
        processname = 'nicos-cache',
        interval = 1.0,
        pollinterval = None,
        unit = 'percent',
    ),
    cache_avg = device(code_base + 'avg.BaseAvg',
        description = 'avg for cache',
        dev = 'cache',
        unit = 'percent',
    ),
    all = device(code_base + 'psutil.CPUPercentage',
        description = 'all CPU utilization',
        index = -1,
        interval = 1.0,
        pollinterval = None,
        unit = 'percent',
    ),
    all_avg = device(code_base + 'avg.BaseAvg',
        description = 'avg for all',
        dev = 'all',
        unit = 'percent',
    ),
)
