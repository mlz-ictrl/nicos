description = 'Email and SMS notifiers'

group = 'lowlevel'

display_order = 99

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Email notifier',
        sender = 'boa@psi.ch',
        copies = [
            ('pierre.boillat@psi.ch', 'important'),
        ],
        subject = 'BOA',
    ),
    warning = device('nicos.devices.notifiers.Mailer',
        description = 'Watchdog email notifier',
        sender = 'boa@psi.ch',
        copies = [
            ('pierre.boillat@psi.ch', 'all'),
        ],
        subject = 'BOA',
    ),
)
