description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'spodi@frm2.tum.de',
                      copies = [('markus.hoelzel@frm2.tum.de', 'all'),   # gets all messages
                                ('anatoliy.senishyn@frm2.tum.de', 'all'),   # gets all messages
                                ('josef.pfanzelt@frm2.tum.de', 'important')], # gets only important messages
                      subject = 'SPODI',
                      mailserver ='mailhost.frm2.tum.de',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
