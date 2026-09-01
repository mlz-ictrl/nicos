description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'puma@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jitae.park@frm2.tum.de', 'all'),
            ('yongjin.kim@frm2.tum.de', 'all'),
            ('jana.pasztorova@kit.edu', 'all'),
        ],
        subject = 'PUMA',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'Reports via SMS',
        server = 'triton.admin.frm2.tum.de',
        receivers = ['017680508564'],
        subject = 'PUMA',
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'puma@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'PUMA log space runs full',
    ),
)
