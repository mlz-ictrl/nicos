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
# 'priority' -- normal priorities are 1 or 2, where 2 is more severe (default 1)
#     priority 0 does not emit warnings (useful together with 'pausecount'
#     for conditions that should block counting but are not otherwise errors)
# 'pausecount' -- if True, the count loop should be paused on the condition
#     (default False)
# 'action' -- code to execute if condition is true (default no code is executed)
watchlist = [
    dict(condition = 't_in_memograph_kws123_value > 3',
         message = 'Temperatur zu hoch (T_in KWS-123)',
         priority = 1,
         gracetime = 5),
]

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'ictrl@frm2.tum.de',
                      receivers = ['alexander.lenz@frm2.tum.de'],
                      subject = 'NICOS Warning',
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                     ),

    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'localhost:14869',
                      notifiers = {1:['email']},
                      mailreceiverkey = 'email/receivers',
                      watch = watchlist,
                     ),
)
