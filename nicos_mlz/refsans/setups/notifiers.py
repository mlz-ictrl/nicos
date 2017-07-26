description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('nicos.devices.notifiers.Mailer',
                      mailserver = 'mailhost.frm2.tum.de',
                      sender = 'refsans@frm2.tum.de',
                      copies = [('matthias.pomm@hzg.de', 'all'),   # gets all messages
                                ('martin.haese@hzg.de', 'important')],
                      subject = 'NICOS',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('nicos.devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = ['01799553828'],
                      lowlevel = True,
                     ),
)
