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
    dict(condition = 'magnet_lhl_value < 6',
         precondtion = 'magnet_lhl_value > 30',
         precondtime = 600,
         gracetime = 60,
         message = 'Helium level too low (ramp down magnet immediatelly)',
         type = 'default',
        # action = 'maw(T, 290)',
     ),
     dict(condition = 'magnet_lhl_value < 6 and B_main_value > 0.1',
         precondtion = 'magnet_lhl_value > 30',
         precondtime = 600,
         gracetime = 300,
         message = 'No helium and field in magnet, ramping automatically down!',
         type = 'critical',
         scriptaction = 'immediatestop',
         action = 'move(B_main, 0)',
     ),
     dict(condition = 'T_ambient_value > 296.5',
         gracetime = 300,
         message = 'Too warm in the room, is AC on?!',
         type = 'default',
     ),
]

includes = ['notifiers']

# The Watchdog device has two lists of notifiers, one for priority 1 ('default')
# and one for priority 2 ('critical').

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'kfes64.troja.mff.cuni.cz:14869',
        notifiers = {'default': ['slacker'],
                     'critical': ['slacker']},
        watch = watchlist,
        loglevel = 'info',
    ),
)
