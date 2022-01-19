description = 'Email notifier example'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        sender = 'saphir@frm2.tum.de.',
        copies = [
            ('nicolas.walte@frm2.tum.de', 'all'),   # gets all messages
            ('walter.hulm@frm2.tum.de', 'important'), # gets only important messages
        ],
        mailserver = 'mailhost.frm2.tum.de',  # please adapt!
        subject = 'NICOS at SAPHiR',
    ),
)
