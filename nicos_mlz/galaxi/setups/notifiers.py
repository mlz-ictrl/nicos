description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'E-Mail notifier',
        mailserver = 'mail.fz-juelich.de',
        sender = 'noreply@fz-juelich.de',
        copies = [
            ('u.ruecker@fz-juelich.de', 'all'),
            ('e.kentzinger@fz-juelich.de', 'important'),
            ('l.fleischhauer-fuss@fz-juelich.de', 'important'),
        ],
        subject = '[NICOS] GALAXI',
    ),
)
