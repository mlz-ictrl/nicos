description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    wemail = device('nicos.devices.notifiers.Mailer',
                    sender = 'laue@frm2.tum.de',
                    copies = [('bjoern.pedersen@frm2.tum.de', 'all')],
                    subject = 'NICOS Warning',
                    lowlevel = True,
                   ),

    email    = device('nicos.devices.notifiers.Mailer',
                      sender = 'laue@frm2.tum.de',
                      copies = [],
                      subject = 'NICOS',
                      lowlevel = True,
                     ),

    smser    = device('nicos.devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
