description = 'Setup for the GALAXI watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(
        setup = 'bruker_axs',
        condition = 'stigmator_current_value > 400.',
        message = 'Stigmator current exceeds 400 mA',
        type = 'default',
    ),
    dict(
        setup = 'bruker_axs',
        condition = 'vacuum_pressure_value > 3.0e-06',
        message = 'Vacuum pressure exceeds 3.0E-6 mbar',
        type = 'default',
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost:14869',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
