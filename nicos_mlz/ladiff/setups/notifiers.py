description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'ladiff@frm2.tum.de',
        copies = [
            ('rgeorgii@frm2.tum.de', 'all'),
            ('markos.skoulatos@frm2.tum.de', 'all'),
        ],
        subject = 'LaDiff',
        mailserver='mailhost.frm2.tum.de',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'Reports via SMS',
        server = 'triton.admin.frm2.tum.de',
        receivers = ['01719251564'],
        subject = 'LaDiff',
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'ladiff@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'LaDiff log space runs full',
    ),
)
