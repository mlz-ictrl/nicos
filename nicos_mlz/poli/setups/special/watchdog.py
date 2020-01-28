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
    dict(condition = '( fugwatch_value == "on" and'
                     '  abs(t_setpoint - ts_value) > 1.5 )',
         type = 'default',
         message = 'Temperature deviation between setpoint and value '
                   'is too high shutting down high voltage.',
         setup = 'highvoltage',
         action = 'maw(fug, 0)',
        ),
    dict(condition = 'ccm8v_lhe_value < 30',
         type = 'se',
         setup = 'ccm8v',
         message = '8T Magnet: He level below 30%',
        ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'se': ['email', 'email_se'],
}

devices = dict(
    email_se = device('nicos.devices.notifiers.Mailer',
        sender = 'poli@frm2.tum.de',
        copies = [
            ('al.weber@fz-juelich.de', 'all'),
            ('d.vujevic@fz-juelich.de', 'all'),
            ('h.korb@fz-juelich.de', 'all'),
            ('v.rubanskyi@fz-juelich.de', 'all'),
        ],
        subject = 'POLI SE',
        mailserver = 'mailhost.frm2.tum.de',
        private = True,
    ),

    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost:14869',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watchlist,
    ),
)
