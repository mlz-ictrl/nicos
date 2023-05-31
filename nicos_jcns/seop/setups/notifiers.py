description = 'Email notifier'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.HostnameMailer',
        mailserver = 'mail.fz-juelich.de',
        sender = 'seop@fz-juelich.de',
        subject = 'SEOP',
        copies = [
            ('e.babcock@fz-juelich.de', 'all'),
            ('z.salhi@fz-juelich.de', 'all'),
        ],
    ),
)
