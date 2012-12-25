description = 'setup for the NICOS watchdog'
group = 'special'

# The entries in this list are dictionaries. Possible keys:
#
# 'setup' -- setup that must be loaded (default '' to mean all setups)
# 'condition' -- condition for warning (a Python expression where cache keys
#    can be used: t_value stands for t/value etc.
# 'gracetime' -- time in sec allowed for the condition to be true without
#    emitting a warning (default no gracetime)
# 'message' -- warning message to display
# 'priority' -- 1 or 2, where 2 is more severe (default 1)
# 'action' -- code to execute if condition is true (default no code is executed)

watchlist = [
    dict(condition = 't_value > 100',
         message = 'Temperature too high',
         priority = 1,
         action = 'maw(T, 0)'),
    dict(condition = 'phi_value > 100 and mono_value > 1.5',
         message = 'phi angle too high for current mono setting',
         gracetime = 5),
]


devices = dict(
    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'localhost:14869',
                      notifiers_1 = [],
                      notifiers_2 = [],
                      watch = watchlist,
                     ),
)
