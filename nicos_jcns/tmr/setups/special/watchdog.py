description = 'setup for the TMR NICOS watchdog'
group = 'special'

watch_conditions = []

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
