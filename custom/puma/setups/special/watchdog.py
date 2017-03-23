description = 'setup for the NICOS watchdog'
group = 'special'

# The entries in this list are dictionaries. Possible keys:
#
# 'setup' -- setup that must be loaded (default '' to mean all setups)
# 'condition' -- condition for warning (a Python expression where cache keys
#    can be used: t_value stands for t/value etc.
# 'gracetime' -- time in sec allowed for the condition to be true without
#    emitting a warning (default 5 sec)
# 'message' -- warning message to display
# 'priority' -- 1 or 2, where 2 is more severe (default 1)
# 'action' -- code to execute if condition is true (default no code is executed)

watchlist = [
    dict(condition = 'fpg2_value == "out"',
         message = 'test warning / just a test / everything is fine',
	 gracetime = 0,
         type = 'critical',
	 ),
#    dict(condition = 'T_value > 299',
#         message = 'temperature cooling?',
#         type = 'critical',
#	 setup = 'lakeshore'
#	 ),
]

includes = ['notifiers', ]

# The Watchdog device has two lists of notifiers, one for priority 1 and
# one for priority 2.

devices = dict(
    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'pumahw.puma.frm2:14869',
                      notifiers = {'default': ['email'],
                                   'critical': ['email', 'smser']},
                      watch = watchlist,
                     ),
)
