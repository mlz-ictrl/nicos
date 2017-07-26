description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
                   sender = 'stressi@frm2.tum.de',
                   copies = [('michael.hofmann@frm2.tum.de', 'all'),  # gets all messages
                             ('weimin.gan@hzg.de', 'all'),  # gets all messages
                             ('joana.kornmeier@frm2.tum.de', 'important'),  # gets only important messages
                            ],
                   subject = 'STRESS-SPEC',
                   lowlevel = True,
                   mailserver ='mailhost.frm2.tum.de',
                  ),
    hvemail = device('nicos.devices.notifiers.Mailer',
                     sender = 'stressi@frm2.tum.de',
                     copies = [('michael.hofmann@frm2.tum.de', 'all'),  # gets all messages
                               ('weimin.gan@hzg.de', 'all'),  # gets all messages
                               ('karl.zeitelhack@frm2.tum.de', 'important'),
                               ('ilario.defendi@frm2.tum.de', 'important'),
                               ('joana.kornmeier@frm2.tum.de', 'important'),  # gets only important messages
                              ],
                     subject = 'STRESS-SPEC',
                     lowlevel = True,
                     mailserver ='mailhost.frm2.tum.de',
                    ),
    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('nicos.devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
