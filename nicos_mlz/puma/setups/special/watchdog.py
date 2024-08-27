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
        condition = 'mtt_status[0] == NOTREACHED',
        message = "'mtt' axis move timed out. Positioning problem? Mobile block?",
        # gracetime = 3,
        type = 'critical',
    ),
    # dict(
        # condition = 'ReactorPower_value > 0.5',
        # message = "Reactor started?",
        # # gracetime = 3,
        # type = 'critical',
    # ),
]

includes = ['notifiers']

devices = dict(
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'puma@frm2.tum.de',
        mailserver = 'smtp.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'PUMA log space runs full',
    ),
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'pumahw.puma.frm2.tum.de:14869',
        notifiers = {
            'default': ['email'],
            'critical': ['email', 'smser'],
            'logspace': ['email', 'smser', 'logspace_notif'],
        },
        watch = watch_conditions,
    ),
)
