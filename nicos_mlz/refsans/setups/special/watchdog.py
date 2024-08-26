description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
pressure_value = 0.018  # no precon
pressure_precon = 0.015
pressure_tag = 'chamber' #'pressure'

# watchlist:
# The entries in this list are dictionaries. Possible keys:
#
# 'setup' -- setup that must be loaded (default '' to mean all setups)
# 'condition' -- condition for warning (a Python expression where cache keys
#    can be used: t_value stands for t/value etc.
# 'gracetime' -- time in sec allowed for the condition to be true without
#    emitting a warning (default 5 sec)
# 'precondition'
#   If present, this condition must be fulfilled for at least ``precondtime``,
#   before condition will trigger. Default is no precondition.
# 'precondtime'
#   The time a precondition must be fulfilled. Default is 5 seconds
# 'message' -- warning message to display
# 'type' -- for defining different types of warnings; this corresponds to the
#     configured notifiers (default 'default')
#     type '' does not emit warnings (useful together with scriptaction)
# 'scriptaction' -- 'pausecount' to pause the count loop on the condition
#     or 'stop' or 'immediatestop' to cancel script execution
#     (default '')
# 'action' -- code to execute if condition is true (default no code is executed)
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'logspace',
         gracetime = 30,
    ),
    dict(condition = 'reactorpower_value < 19.0 or sixfold_value == "closed" or'
                     ' nl2b_value == "closed"',
         precondition = 'sixfold_value == "open" and '
                        'nl2b_value == "open" and '
                        'reactorpower_value > 119.8',
         message = 'Reactor power falling or Sixfold or NL2b closed',
         type = 'critical',
    ),
    # dict(
    #     condition = 'reactorpower_value < 0.1',
    #     message = 'reactorpower_value < 0.1',
    #     type = 'critical',
    # ),
    # dict(
    #     condition = '(sixfold_value == "closed" or nl2b_value == "closed") '
    #     'and reactorpower_value > 19.1',
    #     message = 'NL2b or sixfold shutter closed',
    #     type = 'critical',
    # ),
    dict(condition = f'{pressure_tag}_CB_value > {pressure_value:.3f}',
         precondition = f'{pressure_tag}_CB_value <= {pressure_precon:.3f}',
         message = f'{pressure_tag}_CB_value > {pressure_value:.3f}',
         type = 'critical',
    ),
    dict(condition = f'{pressure_tag}_SFK_value > {pressure_value:.3f}',
         precondition = f'{pressure_tag}_SFK_value <= {pressure_precon:.3f}',
         message = f'{pressure_tag}_SFK_value > {pressure_value:.3f}',
         type = 'critical',
    ),
    dict(condition = f'{pressure_tag}_SR_value > {pressure_value:.3f}',
         precondition = f'{pressure_tag}_SR_value <= {pressure_precon:.3f}',
         message = f'{pressure_tag}_SR_value > {pressure_value:.3f}',
         type = 'critical',
    ),
    dict(
         condition = 't_memograph_in_value > 25',
         message = 'Cooling water temperature greater than 25 C',
         type = 'critical',
         priority = 2,
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email', 'smser'],
    'logspace': ['email', 'smser', 'logspace_notif'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
