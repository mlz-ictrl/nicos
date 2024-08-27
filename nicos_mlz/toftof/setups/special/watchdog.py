description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'loglevel',
         gracetime = 30,
         setup = 'system',
    ),
    dict(
        condition = '(sixfold_value == "closed" or nl2a_value == "closed") '
        'and reactorpower_value > 19.1',
        message = 'NL2a or sixfold shutter closed',
        type = 'critical',
        setup = 'nl2a',
    ),
    dict(
        condition = 'ch_value < 140',
        message = 'Choppers are down! DO SOMETHING!',
        setup = 'chopper',
    ),
    dict(
        condition = 'flow_in_ch_cooling_value < 10',
        message = 'Cooling water flow is less than 10 l/min',
        setup = 'choppermemograph',
    ),
    dict(
        condition = 't_in_ch_cooling_value > 25',
        message = 'Cooling water temperature greater than 25 C',
        setup = 'choppermemograph',
    ),
    dict(
        condition = 'leak_ch_cooling_value > 3',
        message = 'There is a leak in the chopper cooling system',
        setup = 'choppermemograph',
    ),
    dict(
        condition = 'flow_in_chopper_value < 15',
        message = 'The flow in the chopper cooling system is too low',
        setup = 'choppermemograph',
    ),
    dict(
        condition = 't_in_chopper_value > 30',
        message = 'The temperature in the chopper cooling system is too high',
        setup = 'choppermemograph',
    ),
    dict(
        condition = "water_level_chopper_value != 'OK'",
        message = 'The water level in the chopper cooling level is too low',
        setup = 'choppermemograph',
    ),
]

includes = ['notifiers']

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'tofhw.toftof.frm2.tum.de:14869',
        notifiers = {
            'default': ['emailer'],
            'logspace': ['emailer', 'logspace_notif'],
        },
        watch = watch_conditions,
        mailreceiverkey = 'emailer/receivers',
    ),
)
