description = 'Email and SMS notifiers'
group = 'lowlevel'
display_order = 90

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'reseda@frm2.tum.de',
        receivers = [
            'johanna.jochum@frm2.tum.de',
        ],
        copies = [
            ('christian.fuchs@frm2.tum.de', 'important'),
        ],
        subject = 'NICOS@RESEDA',
    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
    # slacker = device('nicos.devices.notifiers.slack.Slacker',
    #     receivers = ['#nicos_build-up'],
    #     authtoken = secret('slack'),
    # ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'reseda@frm2.tum.de',
        mailserver = 'smtp.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'RESEDA log space runs full',
    ),
)
