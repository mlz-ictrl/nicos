description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      description = 'Notifications via email',
                      sender = 'mephisto@frm2.tum.de',
                      copies = [('kathrin.lehmann@frm2.tum.de', 'all'),
                                ('jens.klenke@frm2.tum.de', 'all'),
                               ],
                      mailserver ='mailhost.frm2.tum.de',
                      subject = 'MEPHISTO',
                     ),

    smser    = device('devices.notifiers.SMSer',
                      description = 'Reports via SMS',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
