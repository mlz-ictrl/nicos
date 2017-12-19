description = 'Email notifier'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'cspec@esss.se',
        copies = [
            ('pascale.deen@esss.se', 'all'),
            ('wiebke.lohstroh@frm2.tum.de', 'important'),
            ('slongeville@cea.fr', 'important'),
        ],
        mailserver = 'mailserver.esss.se',  # please adapt!
        subject = 'NICOS at CSPEC',
        lowlevel = True,
    ),
)
