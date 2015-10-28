description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    wemail = device('devices.notifiers.Mailer',
                    sender = 'laue@frm2.tum.de',
                    copies = [('bjoern.pedersen@frm2.tum.de', 'all')],
                    subject = 'NICOS Warning',
                    lowlevel = True,
                   ),

    email    = device('devices.notifiers.Mailer',
                      sender = 'laue@frm2.tum.de',
                      copies = [],
                      subject = 'NICOS',
                      lowlevel = True,
                     ),

    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
