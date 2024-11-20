description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'moke@frm2.tum.de',
        copies = [('s.puetter@fz-juelich.de', 'all'),
                  ('k.kholostov@fz-juelich.de', 'all')],
        subject = 'MOKE',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [],
    ),
)
