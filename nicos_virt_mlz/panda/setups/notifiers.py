description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'vpanda@frm2.tum.de',
        copies = [],
        subject = '[VPANDA]',
    ),
)
