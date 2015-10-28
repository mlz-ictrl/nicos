description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'nectar@frm2.tum.de',
                      copies = [('Christoph.Genreith@frm2.tum.de', 'all'),
                                ('thomas.buecherl@tum.de', 'all'),
                               ],
                      subject = '[NECTAR]',
                      mailserver = 'smtp.frm2.tum.de',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
