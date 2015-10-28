description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      sender = 'kws1@frm2.tum.de',
                      copies = [('g.brandl@fz-juelich.de', 'all'),   # for now
                               ],
                      subject = '[KWS-1]',
                      mailserver = 'mailhost.frm2.tum.de',
                      lowlevel = True,
                     ),

    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
