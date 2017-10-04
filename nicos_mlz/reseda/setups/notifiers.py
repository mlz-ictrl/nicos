description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'reseda@frm2.tum.de',
        receivers = [
            'christian.franz@frm2.tum.de', 'thorsten.schroeder@frm2.tum.de'
        ],
        subject = 'NICOS',
        lowlevel = True,
    ),

    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
        lowlevel = True,
    ),
    slacker = device('nicos.devices.notifiers.Slacker',
        receivers = ['#nicos_build-up'],
        lowlevel = True,
    ),
)
