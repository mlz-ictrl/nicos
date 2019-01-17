description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'mira@frm2.tum.de',
        copies = [('rgeorgii@frm2.tum.de', 'all')],
        subject = 'MIRA',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'Reports via SMS',
        server = 'triton.admin.frm2',
        receivers = ['01719251564'],
    ),
)
