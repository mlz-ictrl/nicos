description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    emailer = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'se-trouble@frm2.tum.de',
        copies = [
            ('al.weber@fz-juelich.de', 'all'),
            ('d.vujevic@fz-juelich.de', 'all'),
            ('h.korb@fz-juelich.de', 'all'),
        ],
        subject = '[NICOS] SE',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
