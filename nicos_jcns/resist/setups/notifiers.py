description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'jcns@frm2.tum.de',
        copies = [('g.brandl@fz-juelich.de', 'all')],
        subject = 'Sample prep lab',
    ),
)
