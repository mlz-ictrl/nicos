description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_value < .5',
         message = 'Disk space for the log files becomes too low.',
         type = 'critical',
         gracetime = 30,
    ),
    dict(
        condition = '(sixfold_value == "closed" or nl5_value == "closed") '
        'and reactorpower_value > 19.1',
        message = 'NL5 or sixfold shutter closed',
        type = 'critical',
    ),
    dict(
        condition = 'selector_speed_value < 6000',
        message = 'Problem with selector. Value below 6000rpm',
        gracetime = 2,
    ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.host'),
        notifiers = {'default': []},
        watch = watch_conditions,
        mailreceiverkey = 'email/receivers',
    ),
)
