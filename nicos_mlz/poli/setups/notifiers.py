description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'poli@frm2.tum.de',
        copies = [
            ('vladimir.hutanu@frm2.tum.de', 'all'),
            ('hao.deng@frm2.tum.de', 'all'),
            ('g.brandl@fz-juelich.de', 'all'),
        ],
        subject = 'POLI NICOS',
        mailserver = 'mailhost.frm2.tum.de',
    ),

    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
    ),
)
