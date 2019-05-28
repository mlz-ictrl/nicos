description = 'setup for the NICOS watchdog'
group = 'special'

# The entries in this list are dictionaries. Possible keys:
#
# 'setup' -- setup that must be loaded (default '' to mean all setups)
# 'condition' -- condition for warning (a Python expression where cache keys
#    can be used: t_value stands for t/value etc.
# 'gracetime' -- time in sec allowed for the condition to be true without
#    emitting a warning (default 5 sec)
# 'precondition'
#   If present, this condition must be fullfiled for at least ``precondtime``,
#   before condition will trigger. Default is no precondition.
# 'precondtime'
#   The time a precondition must be fulfilled. Default is 5 seconds.
# 'message' -- warning message to display
# 'type' -- for defining different types of warnings; this corresponds to the
#   configured notifiers (default 'default')
#   type '' does not emit warnings (useful together with scriptaction)
# 'scriptaction' -- 'pausecount' to pause the count loop on the condition
#   or 'stop' or 'immediatestop' to cancel script execution
#   (default '')
# 'action' -- code to execute if condition is true (default no code is executed)

watchlist = [
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
    dict(condition = 't_value > 300',
         message = 'Temperature too high (exceeds 300 K)',
         type = 'critical',
         gracetime = 1,
         action = 'maw(T, 290)'),
    dict(condition = 'phi_value > 100 and mono_value > 2.5',
         message = 'phi angle too high for current mono setting',
         gracetime = 5),
    dict(condition = 'tbefilter_value > 75',
         scriptaction = 'pausecount',
         setup = 'tas',
         message = 'Beryllium filter temperature too high',
         gracetime = 0),
    dict(condition = 'shutter_value == "closed"',
         type = '',
         scriptaction = 'pausecount',
         message = 'Instrument shutter is closed',
         gracetime = 0),
    dict(condition = 'vacuum_value > 0.2',
         precondition = 'vacuum_value < 0.2',
         setup = 'vacuum',
         message = 'vacuum_value > 0.2 mbar',
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

# The Watchdog device has two lists of notifiers, one for priority 1 ('default')
# and one for priority 2 ('critical').

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost:14869',
        notifiers = {'default': [],
                     'critical': []},
        watch = watchlist,
        loglevel = 'info',
    ),
)
