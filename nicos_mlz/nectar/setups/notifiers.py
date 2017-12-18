description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'nectar@frm2.tum.de',
        copies = [
            ('malgorzata.makowska@frm2.tum.de', 'all'),
            ('thomas.buecherl@tum.de', 'all'),
        ],
        subject = '[NECTAR]',
        mailserver = 'mailhost.frm2.tum.de',
        lowlevel = True,
    ),

    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
        lowlevel = True,
    ),
)
