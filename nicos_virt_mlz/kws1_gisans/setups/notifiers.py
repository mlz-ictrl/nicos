description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'vkws@frm2.tum.de',
        copies = [
        ],
        subject = '[VKWS]',
    ),
)
