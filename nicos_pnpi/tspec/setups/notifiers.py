description = 'Email and SMS notifier'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
                   sender = 'pshcyrill@lns.pnpi.spb.ru',
                   copies = [
                       # gets all messages
                       # ('nobody@example.host', 'all'),
                       # gets only important messages
                       # ('nobody@example.host', 'important'),
                   ],
                   mailserver = 'lns.pnpi.spb.ru',
                   subject = 'NICOS',
                   ),
)
