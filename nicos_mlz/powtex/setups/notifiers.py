description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        description = 'e-mail notifier',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'powtex@frm2.tum.de',
        copies = [('christian.randau@frm2.tum.de', 'all')],
        subject = 'NICOS Warning POWTEX',
    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
