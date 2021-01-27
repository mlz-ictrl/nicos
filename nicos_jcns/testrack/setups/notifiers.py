description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'jcns@frm2.tum.de',
        copies = [],
        subject = 'Testrack',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
    ),
)
