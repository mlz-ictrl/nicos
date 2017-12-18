description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'ictrl@frm2.tum.de',
        receivers = ['alexander.lenz@frm2.tum.de'],
        subject = 'NICOS Warning',
        lowlevel = True,
    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
        lowlevel = True,
    ),
)
