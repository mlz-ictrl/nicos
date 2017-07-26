description = 'Email and SMS notifier settings'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('nicos.devices.notifiers.Mailer',
                      sender = 'treff@frm2.tum.de',
                      copies = [('andreas.ofner@frm2.tum.de', 'all'),
                                ('e.vezhlev@fz-juelich.de', 'all'),
                                ('peter.link@frm2.tum.de', 'important'),
                                ('stefan.mattauch@fz-juelich.de', 'important'),
                                ('c.felder@fz-juelich.de', 'important'),
                                ('alerts.sw.zea2@fz-juelich.de', 'important'),
                               ],
                      subject = '[NICOS] TREFF',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('nicos.devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
