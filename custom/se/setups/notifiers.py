description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    emailer = device('devices.notifiers.Mailer',
                     sender = 'se-trouble@frm2.tum.de',
                     copies = [],
                     subject = 'SE',
                     lowlevel = True,
                    ),

    smser   = device('devices.notifiers.SMSer',
                     server = 'triton.admin.frm2',
                     receivers = [],
                     lowlevel = True,
                    ),
)
