description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
     dict(condition = 'reactorpower_value < 10',
          precondition = 'reactorpower_value > 19.1',
          precondtime = 600,
          message = 'Reactor power too low',
          type = 'critical',
          scriptaction = 'stop',
          gracetime = 300,
         ),
]

includes = ['notifiers']

notifiers = {
    'default': ['wemail'],
    'critical': ['wemail', 'smser'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'lauectrl.laue.frm2.tum.de',
        notifiers = notifiers,
        mailreceiverkey = 'wemail/receivers',
        watch = watch_conditions,
    ),
)
