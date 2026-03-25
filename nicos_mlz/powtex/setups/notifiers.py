description = 'Notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'e-mail notifier',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'powtex@frm2.tum.de',
        copies = [('g.brandl@fz-juelich.de', 'all')],
        subject = '[NICOS] POWTEX',
    ),
)
