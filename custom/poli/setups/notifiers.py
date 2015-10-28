description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'vladimir.hutanu@frm2.tum.de',
                      copies = [('vladimir.hutanu@frm2.tum.de', 'all'),
                                ('andrew.sazonov@frm2.tum.de', 'all'),
                                ('alerts.sw.zea2@fz-juelich.de', 'important'),
                               ],
                      subject = 'POLI NICOS',
                      mailserver = 'mailhost.frm2.tum.de',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
