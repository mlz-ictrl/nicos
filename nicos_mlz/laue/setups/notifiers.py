description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    wemail = device('nicos.devices.notifiers.Mailer',
        sender = 'laue@frm2.tum.de',
        copies = [('bjoern.pedersen@frm2.tum.de', 'all')],
        subject = 'NICOS Warning',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'laue@frm2.tum.de',
        copies = [],
        subject = 'NICOS',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
