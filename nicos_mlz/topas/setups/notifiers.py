description = 'Email notifier'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'e-mail notifier',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'topas@frm2.tum.de',
        copies = [
            ('m.stekiel@fz-juelich.de', 'all'),
            ('g.brandl@fz-juelich.de', 'all'),
        ],
        subject = '[NICOS] TOPAS',
    ),
    mattermost = device('nicos.devices.notifiers.mattermost.Mattermost',
        description = 'mattermost notifier',
        baseurl = 'https://iffchat.fz-juelich.de',
        username = 'topas',
        hookid = secret('mattermost-hookid'),
    ),
)
