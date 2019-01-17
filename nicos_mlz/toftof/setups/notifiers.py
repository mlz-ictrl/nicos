description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    emailer = device('nicos.devices.notifiers.Mailer',
        description = 'Notifier service to send emails',
        sender = 'toftof@frm2.tum.de',
        copies = [
            ('wiebke.lohstroh@frm2.tum.de', 'all'),
            ('marcell.wolf@frm2.tum.de', 'all'),
        ],
        subject = 'TOFTOF',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'Notifier service to send SMS',
        server = 'triton.admin.frm2',
        # receivers = [],
    ),
)
