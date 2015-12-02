description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      description = 'Reports via email',
                      sender = 'reseda@frm2.tum.de',
                      receivers = ['christian.franz@frm2.tum.de',
                                   'thorsten.schroeder@frm2.tum.de'],
                      subject = 'Warning',
                      lowlevel = True,
                     ),
)
