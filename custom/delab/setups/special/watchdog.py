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
# 'action' -- code to execute if condition is true (default no code is executed)
# 'type' -- selects notifiers from configured lists

watchlist = [
#    dict(condition = 'cooltemp_value > 30',
#         message = 'Cooling water temperature exceeds 30 C',
#    ),
#    dict(condition = 'psdgas_value == "empty"',
#         message = 'PSD gas is empty, change bottle!',
#         setup = 'cascade',
#    ),
#    dict(condition = 'tbe_value > 70',
#         message = 'Be filter temperature > 70 K, check cooling',
#    ),
]


devices = dict(
    email    = device('devices.notifiers.Mailer',
                      sender = 'karl.zeitelhack@frm2.tum.de',
                      copies = [('karl.zeitelhack@frm2.tum.de', 'all')],
                      subject = 'DEL Warning',
                     ),

#    smser    = device('devices.notifiers.SMSer',
#                      server = 'triton.admin.frm2',
#                      receivers = ['01719251564', '01782979497'],
#                     ),

    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'localhost',
                      notifiers = {'default': ['email']},
                      watch = watchlist,
                      mailreceiverkey = 'email/receivers',
                     ),
)
