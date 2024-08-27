description = 'setup for the NICOS watchdog'
group = 'special'

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
    dict(
        condition = 'reactorpower_value < 10',
        precondition = 'reactorpower_value > 19.1',
        precondtime = 600,
        message = 'Reactor power too low',
        type = 'critical',
        # action = 'stop()',
        gracetime = 300,
        setup = 'reactor',
    ),
    dict(
        condition = 'hv1_value < 3000',
        precondition = 'hv1_value > 3150',
        precondtime = 600,
        message = 'High voltage problem (anode voltage felt down)',
        type = 'highvoltage',
        gracetime = 5,
        setup = 'detector',
    ),
    dict(
        condition = 'hv2_value > -2300',
        precondition = 'hv1_value < -2450',
        precondtime = 600,
        message = 'High voltage problem (drift voltage felt down)',
        type = 'highvoltage',
        gracetime = 5,
        setup = 'detector',
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email', 'smser'],
    'highvoltage': ['hvemail', 'smser'],
    'logspace': ['email', 'smser', 'logspace_notif'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'stressictrl.stressi.frm2.tum.de',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
