description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
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
        watch = watch_conditions,
    ),
)
