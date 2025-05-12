description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'e-mail notifier',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'biodiff@frm2.tum.de',
        copies = [
            ('t.schrader@fz-juelich.de', 'all'),
            ('andreas.ostermann@frm2.tum.de', 'all'),
            ('c.felder@fz-juelich.de', 'important'),
        ],
        subject = '[NICOS] BIODIFF',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'SMS notifier',
        server = 'triton.admin.frm2.tum.de',
        receivers = ['01736746111', '015146192359'],
    ),
)
