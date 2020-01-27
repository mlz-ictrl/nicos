description = 'setup for the NICOS watchdog'
group = 'special'

# watchlist:
# The entries in this list are dictionaries. Possible keys:
#
# 'setup' -- setup that must be loaded (default '' to mean all setups)
# 'condition' -- condition for warning (a Python expression where cache keys
#    can be used: t_value stands for t/value etc.
# 'gracetime' -- time in sec allowed for the condition to be true without
#    emitting a warning (default 5 sec)
# 'message' -- warning message to display
# 'type' -- for defining different types of warnings; this corresponds to the
#     configured notifiers (default 'default')
#     type '' does not emit warnings (useful together with scriptaction)
# 'scriptaction' -- 'pausecount' to pause the count loop on the condition
#     or 'stop' or 'immediatestop' to cancel script execution
#     (default '')
# 'action' -- code to execute if condition is true (default no code is executed)
watchlist = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'critical',
         gracetime = 30,
        ),
    dict(condition = 'reactorpower_value < 19',
         message = 'Possible Reactor Shutdown! Reactor power < 19MW',
         type = 'critical',
         setup = 'reactor',
         gracetime = 300,
        ),
    dict(condition = 'He_pressure_value < 30',
         message = 'Pressure in He bottle less than 30bar. Please change soon!',
         type = 'default',
         setup = 'reactor',
         gracetime = 300,
        ),
    dict(condition = 'selector_vacuum > 0.005',
         message = 'Selector vacuum above 5E-3mbar!',
         type = 'default',
         setup = 'selector',
         gracetime = 30,
        ),
    dict(condition = 'HomeSpace < 1',
         message = '/home/antares is running out of space. Only 1GB left!',
         type = 'default',
         setup = 'system',
         gracetime = 300,
        ),
    dict(condition = 'DataSpace < 1000',
         message = '/data is running out of space. Only 1TB left!',
         type = 'default',
         setup = 'system',
         gracetime = 300,
        ),
    dict(condition = 'VarSpace < 3',
         message = '/var is running out of space. Only 3GB left!',
         type = 'default',
         setup = 'system',
         gracetime = 300,
        ),
    dict(condition = 'Space < 1',
         message = 'The root directory of antareshw is running out of space. Only 1GB left!',
         type = 'default',
         setup = 'system',
         gracetime = 300,
        ),
    dict(condition = 'amagnet_T1 > 65',
         message = 'amagnet temperature above 65°C',
         type = 'critical',
         setup = 'amagnet',
         gracetime = 60,
         action = 'move(amagnet_current, 0)',
        ),
    dict(condition = 'amagnet_T2 > 65',
         message = 'amagnet temperature above 65°C',
         type = 'critical',
         setup = 'amagnet',
         gracetime = 60,
         action = 'move(amagnet_current, 0)',
        ),
    dict(condition = 'amagnet_T3 > 65',
         message = 'amagnet temperature above 65°C',
         type = 'critical',
         setup = 'amagnet',
         gracetime = 60,
         action = 'move(amagnet_current, 0)',
        ),
    dict(condition = 'amagnet_T4 > 65',
         message = 'amagnet temperature above 65°C',
         type = 'critical',
         setup = 'amagnet',
         gracetime = 60,
         action = 'move(amagnet_current, 0)',
        ),
]

includes = ['notifiers']

notifiers = {
    'default': ['warning', 'smser'],
    'critical': ['warning', 'smser'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watchlist,
    ),
)
