# -*- coding: utf-8 -*-
description = 'Email and SMS notifier'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    mailer    = device('nicos.devices.notifiers.Mailer',
                       sender = 'maria@frm2.tum.de',
                       copies = [('s.mattauch@fz-juelich.de', 'all'),
                                 ('a.koutsioumpas@fz-juelich.de', 'all'),
                                 ('c.felder@fz-juelich.de', 'important'),
                                 ('alerts.sw.zea2@fz-juelich.de', 'important'),
                                ],
                      subject = '[NICOS] MARIA',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('nicos.devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
