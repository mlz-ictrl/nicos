description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'puma@frm2.tum.de',
        mailserver = 'smtp.frm2.tum.de',
        copies = [
            ('jitae.park@frm2.tum.de', 'all'),
            ('norbert.juenke@frm2.tum.de', 'important'),
        ],
        subject = 'PUMA',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'Reports via SMS',
        server = 'triton.admin.frm2.tum.de',
        receivers = ['017680508564'],
    ),
)
