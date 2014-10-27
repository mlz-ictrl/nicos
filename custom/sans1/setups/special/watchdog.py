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
    dict(condition = 'T_in_memograph_value > 20',
         message = 'Cooling water inlet temperature exceeds 20 C, check FAK40 and SANS-1 memograph!',
         #type = 'critical',
    ),
    dict(condition = 'ReactorPower_value < 19',
         message = 'Reactor power is below 19 MW!',
         #type = 'critical',
         gracetime = '300',
    ),
    dict(condition = 'ccmsans_T2_value > 5',
         message = 'Magnet Ch Stage 2 > 5 K, check for possible quench of magnet!',
         #type = 'critical',
         setup = 'ccmsans',
    ),
]


# The Watchdog device has two lists of notifiers, one for priority 1 and
# one for priority 2.

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      sender = 'sebastian.muehlbauer@frm2.tum.de',
                      receivers = ['ralph.gilles@frm2.tum.de', 'sebastian.muehlbauer@frm2.tum.de', 'andre.heinemann@hzg.de'],
                      copies = ['andreas.wilhelm@frm2.tum.de'],
                      subject = 'SANS-1 Warning',
                     ),

#    smser    = device('devices.notifiers.SMSer',
#                      server = 'triton.admin.frm2',
#                      receivers = ['01719251564', '01782979497'],
#                     ),

    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'sans1ctrl.sans1.frm2:14869',
                      notifiers = {'default': ['email'], 'critical': ['email']},
                      watch = watchlist,
                      mailreceiverkey = 'email/receivers',
                     ),
)
