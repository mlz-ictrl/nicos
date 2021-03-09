description = 'Email and SMS notifiers'

group = 'lowlevel'
display_order = 90

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'reseda@frm2.tum.de',
        receivers = [
            'philipp.bender@frm2.tum.de',
            'johanna.jochum@frm2.tum.de'
        ],
        subject = 'NICOS@RESEDA',
    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
    ),
    slacker = device('nicos.devices.notifiers.slack.Slacker',
        receivers = ['#nicos_build-up'],
        keystoretoken = 'slack',
    ),
)
