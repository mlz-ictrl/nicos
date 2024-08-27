
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
    dict(condition = 'stt_value > 100 and mono_value > 2.5',
         message = 'stt angle too high for current mono setting',
         gracetime = 5,
         setup = 'tas'),
    dict(condition = 'tbefilter_value > 75',
         scriptaction = 'pausecount',
         setup = 'tas',
         message = 'Beryllium filter temperature too high',
         gracetime = 0),
    dict(condition = 'shutter_value == "closed"',
         type = '',
         scriptaction = 'pausecount',
         message = 'Instrument shutter is closed',
         gracetime = 0,
         setup = 'tas'),
    dict(condition = 'vacuum_value > 0.2',
         precondition = 'vacuum_value < 0.2',
         setup = 'vacuum',
         message = 'vacuum_value > 0.2 mbar',
         type = 'critical'),
    dict(condition = 'reactorpower_value < 10',
         precondition = 'reactorpower_value > 19.1',
         precondtime = 60,
         setup = 'source',
         message = 'Reactor power too low',
         type = 'critical',
         action = 'stop()',
         gracetime = 30,
         precondcooldown = 30),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost:14869',
        notifiers = {'default': [],
                     'critical': []},
        watch = watch_conditions,
        loglevel = 'info',
    ),
)
