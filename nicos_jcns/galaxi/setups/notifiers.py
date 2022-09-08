description = 'GALAXI e-mail notifiers'
group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via e-mail.',
        mailserver = 'mail.fz-juelich.de',
        sender = 'galaxi@fz-juelich.de',
        copies = [
            ('u.ruecker@fz-juelich.de', 'all'),
            ('e.kentzinger@fz-juelich.de', 'important'),
            ('a.steffens@fz-juelich.de', 'all'),
        ],
        subject = '[GALAXI]',
    ),
)
