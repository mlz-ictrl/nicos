description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'kws2@frm2.tum.de',
        copies = [
            ('g.brandl@fz-juelich.de', 'all'),
            ('a.radulescu@fz-juelich.de', 'all'),
            ('m.s.appavou@fz-juelich.de', 'all'),
            ('j.houston@fz-juelich.de', 'all'),
        ],
        subject = '[KWS-2]',
        mailserver = 'mailhost.frm2.tum.de',
        lowlevel = True,
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2',
        receivers = [],
        lowlevel = True,
    ),
)
