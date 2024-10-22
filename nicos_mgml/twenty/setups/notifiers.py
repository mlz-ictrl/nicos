description = 'Email and SMS notifiers'

group = 'lowlevel'
display_order = 90

devices = dict(
        email = device('nicos.devices.notifiers.Mailer',
                description = 'Reports via email',
                mailserver = 'smtp.karlov.mff.cuni.cz:465',
                security = 'ssl',
                username = '0mgml-panel',
                sender = 'noreply@mgml.eu',
                receivers = [
                        'petr.cermak@matfyz.cuni.cz', 'proschek.petr@gmail.com'
                        ],
                subject = 'NICOS@MGML',
                ),
        slacker = device('nicos.devices.notifiers.slack.Slacker',
                receivers = ['#20t_measurement'],
                authtoken = 'slack',
                ),
        )
