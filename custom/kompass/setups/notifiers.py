description = 'Email and SMS notifier examples'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'kompass@frm2.tum.de',
                      copies = [('alexander.gruenwald@frm2.tum.de', 'all'),   # gets all messages
                                ('georg.waldherr@frm2.tum.de', 'important')], # gets only important messages
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
