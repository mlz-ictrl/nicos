description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
pressure_value = 0.018  # no precon
pressure_precon = 0.015
pressure_tag = 'chamber' #'pressure'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'logspace',
         gracetime = 30,
    ),
    dict(condition = 'reactorpower_value < 19.0 or sixfold_value == "closed" or'
                     ' nl2b_value == "closed"',
         precondition = 'sixfold_value == "open" and '
                        'nl2b_value == "open" and '
                        'reactorpower_value > 119.8',
         message = 'Reactor power falling or Sixfold or NL2b closed',
         type = 'critical',
    ),
    # dict(
    #     condition = 'reactorpower_value < 0.1',
    #     message = 'reactorpower_value < 0.1',
    #     type = 'critical',
    # ),
    # dict(
    #     condition = '(sixfold_value == "closed" or nl2b_value == "closed") '
    #     'and reactorpower_value > 19.1',
    #     message = 'NL2b or sixfold shutter closed',
    #     type = 'critical',
    # ),
    dict(condition = f'{pressure_tag}_CB_value > {pressure_value:.3f}',
         precondition = f'{pressure_tag}_CB_value <= {pressure_precon:.3f}',
         message = f'{pressure_tag}_CB_value > {pressure_value:.3f}',
         type = 'critical',
    ),
    dict(condition = f'{pressure_tag}_SFK_value > {pressure_value:.3f}',
         precondition = f'{pressure_tag}_SFK_value <= {pressure_precon:.3f}',
         message = f'{pressure_tag}_SFK_value > {pressure_value:.3f}',
         type = 'critical',
    ),
    dict(condition = f'{pressure_tag}_SR_value > {pressure_value:.3f}',
         precondition = f'{pressure_tag}_SR_value <= {pressure_precon:.3f}',
         message = f'{pressure_tag}_SR_value > {pressure_value:.3f}',
         type = 'critical',
    ),
    dict(
         condition = 't_memograph_in_value > 25',
         message = 'Cooling water temperature greater than 25 C',
         type = 'critical',
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email', 'smser'],
    'logspace': ['email', 'smser', 'logspace_notif'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
