description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'critical',
         gracetime = 30,
    ),
    dict(
        condition = 'reactorpower_value < 10',
        precondition = 'reactorpower_value > 19.1',
        precondtime = 600,
        message = 'Reactor power too low',
        type = 'critical',
        setup = 'reactor',
        # action = 'stop()',
        gracetime = 300,
    ),
    dict(
        condition = 'hv1_value < 3000',
        precondition = 'hv1_value > 3150',
        precondtime = 600,
        message = 'High voltage problem (anode voltage felt down)',
        type = 'highvoltage',
        setup = 'detector',
        gracetime = 5,
    ),
    dict(
        condition = 'hv2_value > -2300',
        precondition = 'hv1_value < -2450',
        precondtime = 600,
        message = 'High voltage problem (drift voltage felt down)',
        type = 'highvoltage',
        setup = 'detector',
        gracetime = 5,
    ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.host'),
        notifiers = {'default': [],
                     'critical': []},
        watch = watch_conditions,
        loglevel = 'info',
    ),
)
