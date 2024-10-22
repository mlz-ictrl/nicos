description = 'Email and SMS notifiers'

group = 'lowlevel'
display_order = 90

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Reports via email',
        mailserver = '-',
        sender = 'noreply@mgml.eu',
        receivers = [
            'cermak@mag.mff.cuni.cz'
        ],
        subject = 'NICOS@SMARACT',
    ),
    slacker = device('nicos.devices.notifiers.slack.Slacker',
        receivers = ['#smaract'],
        authtoken = 'slack',
    ),
)
