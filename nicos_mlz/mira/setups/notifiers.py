description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'mira@frm2.tum.de',
        copies = [
            ('rgeorgii@frm2.tum.de', 'all'),
            ('markos.skoulatos@frm2.tum.de', 'all'),
        ],
        subject = 'MIRA',
        mailserver='mailhost.frm2.tum.de',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'Reports via SMS',
        server = 'triton.admin.frm2.tum.de',
        receivers = ['01719251564'],
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'mira@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'MIRA log space runs full',
    ),
)
