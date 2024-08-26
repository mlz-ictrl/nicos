description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'The notifier to send emails',
        sender = 'erwin@frm2.tum.de',
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
        mailserver = 'smtp.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'ErwiN log space runs full',
    ),
)
