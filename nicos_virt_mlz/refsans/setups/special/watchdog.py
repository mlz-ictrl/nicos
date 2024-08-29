description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(
        condition = 'reactorpower_value < 19.0 or sixfold_value == "closed" or'
                    ' nl2b_value == "closed"',
        precondition = 'sixfold_value == "open" and '
                       'nl2b_value == "open" and '
                       'reactorpower_value > 19.8',
        precondtime = 120,
        gracetime = 120,
        message = 'Reactor power falling or Sixfold or NL2b closed',
        type = 'critical',
    ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.cache_host'),
        notifiers = {'default': [],
                     'critical': []},
        watch = watch_conditions,
    ),
)
