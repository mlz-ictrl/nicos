description = 'Email notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        mailserver = 'mail.fz-juelich.de',
        sender = 'galaxi@fz-juelich.de',
        copies = [
            ('u.ruecker@fz-juelich.de', 'all'),
            ('e.kentzinger@fz-juelich.de', 'important'),
            ('a.steffens@fz-juelich.de', 'all'),
            ('l.fleischhauer-fuss@fz-juelich.de', 'important'),
        ],
        subject = '[GALAXI]',
    ),
)
