description = 'setup for the NICOS watchdog'

group = 'special'

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.host'),
        notifiers = {},
        mailreceiverkey = 'email/receivers',
        watch = [],
    ),
)
