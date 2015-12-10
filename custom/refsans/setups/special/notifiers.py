description = 'Email and SMS notifier examples'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      mailserver = 'smtp.frm2.tum.de',
                      sender = 'refsans@frm2.tum.de',
                      copies = [('matthias.pomm@hzg.de', 'all'),],   # gets all messages
                      subject = 'NICOS',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = ['01799553828'],
                      lowlevel = True,
                     ),
)
