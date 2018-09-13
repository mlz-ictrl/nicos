description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'peter.stein@frm2.tum.de',
        copies = [('peter.stein@frm2.tum.de', 'all')],
        subject = 'NICOS:helios',
        lowlevel = True,
    ),
    # smser = device('nicos.devices.notifiers.SMSer',
    #     server = 'triton.admin.frm2'
    # ),
)
