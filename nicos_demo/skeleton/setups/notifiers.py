description = 'Email and SMS notifier examples'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'nobody@example.host',
        copies = [
            ('nobody@example.host', 'all'),   # gets all messages
            ('nobody@example.host', 'important'), # gets only important messages
        ],
        mailserver = 'mailserver.host',  # please adapt!
        subject = 'NICOS',
        lowlevel = True,
    ),
)
