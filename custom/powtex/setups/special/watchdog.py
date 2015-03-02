# This setup file configures the nicos poller service.

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
#     type '' does not emit warnings (useful together with 'pausecount'
#     for conditions that should block counting but are not otherwise errors)
# 'pausecount' -- if True, the count loop should be paused on the condition
#     (default False)
# 'action' -- code to execute if condition is true (default no code is executed)
watchlist = []
# watchlist = [
#    dict(condition = 't_value > 100',
#         message = 'Temperature too high',
#         type = 'critical',
#         action = 'maw(T, 0)',
#        ),
#    dict(condition = 'phi_value > 100 and mono_value > 1.5',
#         message = 'phi angle too high for current mono setting',
#         gracetime = 5,
#        ),
# ]

notifiers = {
    'default':  ['email'],
    'critical': ['email'],
}

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('devices.notifiers.Mailer',
                      description = 'E-Mail notifier',
                      sender = 'powtex@frm2.tum.de',
                      copies = [('christian.randau@frm2.tum.de', 'all'),],
                      subject = 'NICOS Warning POWTEX',
                     ),

    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'localhost:14869',
                      notifiers = notifiers,
                      mailreceiverkey = 'email/receivers',
                      watch = watchlist,
                     ),
)
