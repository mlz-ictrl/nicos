description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    emailer  = device('devices.notifiers.Mailer',
                      description = 'Notifier service to send emails',
                      sender = 'toftof@frm2.tum.de',
                      copies = [('wiebke.lohstroh@frm2.tum.de', 'all'),
                               # ('Josef.Huber@frm2.tum.de', 'all'),
                                ('zachary.evenson@frm2.tum.de', 'all'),
                               ],
                      subject = 'TOFTOF',
                      lowlevel = True,
                     ),

    smser    = device('devices.notifiers.SMSer',
                      description = 'Notifier service to send SMS',
                      server = 'triton.admin.frm2',
    #                 receivers = ['01719251564', '01782979497'],
                      lowlevel = True,
                     ),
)
