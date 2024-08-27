description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    # dict(condition = 'cooltemp_value > 30',
    #     message = 'Cooling water temperature exceeds 30 C',
    # ),
    # dict(condition = 'psdgas_value == "empty"',
    #     message = 'PSD gas is empty, change bottle!',
    #     setup = 'cascade',
    # ),
    # dict(condition = 'tbe_value > 70',
    #     message = 'Be filter temperature > 70 K, check cooling',
    # ),
]

includes = ['notifiers']

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost',
        notifiers = {'default': ['email']},
        watch = watch_conditions,
        mailreceiverkey = 'email/receivers',
    ),
)
