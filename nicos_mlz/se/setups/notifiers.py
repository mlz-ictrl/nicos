description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    emailer = device('nicos.devices.notifiers.Mailer',
                     sender = 'se-trouble@frm2.tum.de',
                     copies = [],
                     subject = 'SE',
                     lowlevel = True,
                    ),

    smser   = device('nicos.devices.notifiers.SMSer',
                     server = 'triton.admin.frm2',
                     receivers = [],
                     lowlevel = True,
                    ),
)
