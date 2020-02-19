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
# 'precondition'
#   If present, this condition must be fullfiled for at least ``precondtime``,
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
watchlist = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'critical',
         gracetime = 30,
    ),
    dict(condition = 'reactorpower_value < 19.0 or sixfold_value == "closed" or'
                     ' nl2b_value == "closed"',
         precondition = 'sixfold_value == "open" and '
                        'nl2b_value == "open" and '
                        'reactorpower_value > 19.8',
         message = 'Reactor power falling or Sixfold or NL2b closed',
         type = 'critical',
    ),
    dict(condition = 'pressure_CB_value > 0.2',
         precondition = 'pressure_CB_value < 0.1',
         message = 'pressure_CB_value > 0.2',
         type = 'critical',
        ),
    dict(condition = 'pressure_SFK_value > 0.2',
         precondition = 'pressure_SFK_value < 0.1',
         message = 'pressure_SFK_value > 0.2',
         type = 'critical',
        ),
    dict(condition = 'pressure_SR_value > 0.2',
         precondition = 'pressure_SR_value < 0.1',
         message = 'pressure_SR_value > 0.2',
         type = 'critical',
        ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email', 'smser'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'refsansctrl.refsans.frm2.tum.de',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watchlist,
    ),
)
