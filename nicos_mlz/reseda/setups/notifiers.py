description = 'Email and SMS notifiers'

group = 'lowlevel'
display_order = 90

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'reseda@frm2.tum.de',
        receivers = [
            'christian.franz@frm2.tum.de', 'olaf.soltwedel@frm2.tum.de'
        ],
        subject = 'NICOS@RESEDA',
        lowlevel = True,
    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
        lowlevel = True,
    ),
    slacker = device('nicos.devices.notifiers.slack.Slacker',
        receivers = ['#nicos_build-up'],
        lowlevel = True,
    ),
)
