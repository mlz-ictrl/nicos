description = 'HERMES e-mail notifiers'
group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mail.fz-juelich.de',
        sender = 'hermes@fz-juelich.de',
        copies = [
            ('j.baggemann@fz-juelich.de', 'important'),
            ('u.ruecker@fz-juelich.de', 'all'),
            ('a.steffens@fz-juelich.de', 'all'),
            ('p.zakalek@fz-juelich.de', 'important'),
        ],
        subject = '[NICOS] HERMES',
    ),
)
