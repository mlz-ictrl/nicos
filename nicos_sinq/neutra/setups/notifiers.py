description = 'Email and SMS notifiers'

group = 'lowlevel'

display_order = 99

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Email notifier',
        mailserver='mailsend.psi.ch',
        sender = 'neutra@psi.ch',
        copies = [
            ('pierre.boillat@psi.ch', 'important'),
        ],
        subject = 'NEUTRA',
    ),
    warning = device('nicos.devices.notifiers.Mailer',
        description = 'Watchdog email notifier',
        mailserver='mailsend.psi.ch',
        sender = 'neutra@psi.ch',
        copies = [
            ('pierre.boillat@psi.ch', 'all'),
        ],
        subject = 'NEUTRA',
    ),
)
