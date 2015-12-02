description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('devices.notifiers.Mailer',
                   description = 'E-Mail notifier',
                   sender = 'powtex@frm2.tum.de',
                   copies = [('christian.randau@frm2.tum.de', 'all'),],
                   subject = 'NICOS Warning POWTEX',
                   lowlevel = True,
                  ),
)
