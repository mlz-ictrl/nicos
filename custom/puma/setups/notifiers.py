description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'puma@frm2.tum.de',
                      copies = [('jitae.park@frm2.tum.de', 'all'),   # gets all messages
                                ('oleg.sobolev@frm2.tum.de', 'all'),  # gets all messages
                                ('norbert.juehnke@frm2.tum.de', 'important'),],
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
