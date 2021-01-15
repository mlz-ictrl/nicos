description = 'Email and SMS notifier examples'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'j-nse@frm2.tum.de',
        copies = [
            ('o.holderer@fz-juelich.de', 'all'),
            ('g.brandl@fz-juelich.de', 'all'),
        ],
        subject = 'NICOS',
    ),

    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
    ),
)
