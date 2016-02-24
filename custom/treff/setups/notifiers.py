description = 'Email and SMS notifier settings'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'treff@frm2.tum.de',
                      copies = [('andreas.ofner@frm2.tum.de', 'all'),   # gets all messages
                                ('peter.link@frm2.tum.de', 'important'), # gets only important messages
                                ('stefan.mattauch@fz-juelich.de', 'important'),
                               ],
                      subject = 'NICOS',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
