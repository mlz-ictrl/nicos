description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        sender = 'karl.zeitelhack@frm2.tum.de',
        copies = [('karl.zeitelhack@frm2.tum.de', 'all')],
        subject = 'DEL',
        lowlevel = True,
    ),
    # smser = device('nicos.devices.notifiers.SMSer',
    #     server = 'triton.admin.frm2'
    # ),
)
