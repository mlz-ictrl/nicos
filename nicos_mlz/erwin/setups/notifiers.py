description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'The notifier to send emails',
        sender = 'erwin@frm2.tum.de',
        copies = [('markus.hoelzel@frm2.tum.de', 'all')],
        subject = 'ErwiN',
    ),

    # smser = device('nicos.devices.notifiers.SMSer',
    #     server = 'triton.admin.frm2',
    #     receivers = [],
    # ),
)
