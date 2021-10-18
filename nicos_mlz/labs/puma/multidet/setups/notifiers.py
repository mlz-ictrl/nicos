description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'puma@frm2.tum.de',
        mailserver = 'smtp.frm2.tum.de',
        copies = [
            ('Avishek.Maity@frm2.tum.de', 'all'),
        ],
        subject = 'PUMA',
    ),
)
