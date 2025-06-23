description = 'Email and SMS notifier examples'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'kompass@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('braden@ph2.uni-koeln.de','important'),
            ('manuel.mueller@frm2.tum.de', 'all'),
        ],
        subject = 'NICOS',
    ),

    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
        subject = 'NICOS',
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'kompass@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'KOMPASS log space runs full',
    ),
)
