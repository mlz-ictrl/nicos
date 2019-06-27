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
    dict(
        condition = 'stigmator_current > 400.',
        message = 'Stigmator current exceeds 400 mA',
        type = 'default',
    ),
    dict(
        condition = 'vacuum_pressure > 3.0e-06',
        message = 'Vacuum pressure exceeds 3.0E-6 mbar',
        type = 'default',
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'phys.galaxi.kfa-juelich.de:14869',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watchlist,
    ),
)
