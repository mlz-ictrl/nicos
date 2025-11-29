description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for the log files becomes too low.',
         type = 'critical',
         gracetime = 30,
    ),
    dict(condition = 'Space_status[0] == WARN',
         message = 'Disk space for the data files becomes too low.',
         type = 'critical',
         gracetime = 10,
    ),
    # dict(condition = 't_value > 300',
    #      message = 'Temperature too high (exceeds 300 K)',
    #      type = 'critical',
    #      gracetime = 1,
    #      action = 'maw(T, 290)'),
    # dict(condition = 'shutter_value == "closed"',
    #      type = '',
    #      scriptaction = 'pausecount',
    #      message = 'Instrument shutter is closed',
    #      gracetime = 0),
    dict(condition = 'chamber_pressure_value > 1.',
         precondition = 'chamber_pressure_vacuum_value < 1.',
         setup = 'pressure',
         message = 'chamber pressure > 1 mbar',
         type = 'critical',
        ),
    dict(condition = 'reactorpower_value < 10',
         precondition = 'reactorpower_value > 19.1',
         precondtime = 60,
         setup = 'source',
         message = 'Reactor power too low',
         type = 'critical',
         action = 'stop()',
         gracetime = 30,),
    # dict(condition = 'ReactorPower_value < 19',
    #      # precondition = 'ReactorPower_value >= 19',
    #      pausecount = True,
    #      message = 'Reactor power is lower than 19 MW',
    #      # action = '',
    #      gracetime = 10, ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.cache_host'),
        notifiers = {'default': [],
                     'critical': []},
        watch = watch_conditions,
        loglevel = 'info',
    ),
)
