description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'The notifier to send emails',
        sender = 'firepod@frm2.tum.de',
        copies = [('christoph.hauf@frm2.tum.de', 'all')],
        subject = 'FirePod',
    ),
    # smser = device('nicos.devices.notifiers.SMSer',
    #     server = 'triton.admin.frm2.tum.de',
    #     receivers = [],
    # ),
)
