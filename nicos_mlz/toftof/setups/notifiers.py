description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    emailer = device('nicos.devices.notifiers.Mailer',
        description = 'Notifier service to send emails',
        sender = 'toftof@frm2.tum.de',
        copies = [
            ('christopher.garvey@frm2.tum.de', 'all'),
            ('marcell.wolf@frm2.tum.de', 'all'),
        ],
        subject = 'TOFTOF',
        mailserver = 'mailhost.frm2.tum.de',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'Notifier service to send SMS',
        server = 'triton.admin.frm2.tum.de',
        # Marcell, Chris
        # receivers = [017640710352, 017670806708],
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'toftof@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'TOFTOF log space runs full',
    ),
)
