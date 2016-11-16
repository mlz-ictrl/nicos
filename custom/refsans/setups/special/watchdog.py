# This setup file configures the nicos watchdog service.

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
    dict(condition = '(sixfold_value == "closed" or nl2b_value == "closed") '
                     'and reactorpower_value > 19',
         message = 'NL2b or sixfold shutter closed',
         type = 'critical',
        ),
    dict(condition = 'vacuum_sfk_value > 0.2',
         precondition = 'vacuum_sfk_value < 0.2',
         message = 'vacuum_sfk_value > 0.2',
         type = 'critical',
        ),
    dict(condition = 'vacuum_sr_value > 0.02',
         precondition = 'vacuum_sr_value < 0.02',
         message = 'vacuum_sr_value > 0.02',
         type = 'critical',
        ),
]

includes = ['notifiers', ]

notifiers = {
    'default':  ['email'],
    'critical': ['email', 'smser'],
}

devices = dict(
    Watchdog = device('services.watchdog.Watchdog',
                      # use only 'localhost' if the cache is really running on
                      # the same machine, otherwise use the official computer
                      # name
                      cache = 'refsans10.refsans.frm2',
                      notifiers = notifiers,
                      mailreceiverkey = 'email/receivers',
                      watch = watchlist,
                     ),
)
