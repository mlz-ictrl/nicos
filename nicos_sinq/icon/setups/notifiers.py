description = 'Email and SMS notifiers'

group = 'lowlevel'

display_order = 99

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Email notifier',
        mailserver='smtpint.psi.ch',
        sender = 'icon@psi.ch',
        copies = [
            ('anders.kaestner@psi.ch', 'all'),
        ],
        subject = 'ICON',
    ),
)
