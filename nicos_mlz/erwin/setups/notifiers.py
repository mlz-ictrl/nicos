description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'The notifier to send emails',
        sender = 'erwin@frm2.tum.de',
        mailserver ='mailhost.frm2.tum.de',
        copies = [
            ('markus.hoelzel@frm2.tum.de', 'all'),
        ],
        subject = 'ErwiN',
    ),
    ngmail = device('nicos.devices.notifiers.Mailer',
        sender = 'erwin@frm2.tum.de',
        copies = [
            ('markus.hoelzel@frm2.tum.de', 'all'),   # gets all messages
            ('anatoliy.senyshyn@frm2.tum.de', 'important'),   # gets only important messages
            ('josef.pfanzelt@frm2.tum.de', 'important'), # gets only important messages
            ('christoph.hauf@frm2.tum.de', 'important')
        ],
        subject = 'Erwin/Neutron guide',
        mailserver ='mailhost.frm2.tum.de',
    ),
    # smser = device('nicos.devices.notifiers.SMSer',
    #     server = 'triton.admin.frm2.tum.de',
    #     receivers = [],
    # ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'erwin@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'ErwiN log space runs full',
    ),
    dmail = device('nicos.devices.notifiers.Mailer',
        sender = 'erwin@frm2.tum.de',
        copies = [
            ('markus.hoelzel@frm2.tum.de', 'all'),   # gets all messages
            ('karl.zeitelhack@frm2.tum.de', 'all'),   # gets all messages
            ('ilario.defendi@frm2.tum.de', 'all'),   # gets all messages
            ('alan.howard@frm2.tum.de', 'all'),   # gets all messages
        ],
        subject = 'Erwin/CHARM detector',
        mailserver ='mailhost.frm2.tum.de',
    ),
    dsms = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = ['015170151090'], # Markus
        subject = 'Erwin/CHARM detector',
    ),
)
