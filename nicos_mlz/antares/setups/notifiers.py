description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email = device('nicos.devices.notifiers.Mailer',
        description = 'Email notifier',
        sender = 'antares@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('michael.schulz@frm2.tum.de', 'important'),
            ('tobias.neuwirth@frm2.tum.de', 'important'),
            ('burkhard.schillinger@frm2.tum.de', 'important'),
            ('dominik.bausenwein@frm2.tum.de', 'important'),
        ],
        subject = 'ANTARES',
    ),
    warning = device('nicos.devices.notifiers.Mailer',
        description = 'Watchdog email notifier',
        sender = 'antares@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('michael.schulz@frm2.tum.de', 'all'),
            ('tobias.neuwirth@frm2.tum.de', 'all'),
            ('burkhard.schillinger@frm2.tum.de', 'all'),
            ('dominik.bausenwein@frm2.tum.de', 'all'),
        ],
        subject = 'ANTARES',
    ),
    smser = device('nicos.devices.notifiers.SMSer',
        description = 'SMS notifier',
        receivers = ['015121100909'],
        server = 'triton.admin.frm2.tum.de',
        subject = 'ANTARES',
    ),
    logspace_notif = device('nicos.devices.notifiers.Mailer',
        description = 'Reports about the limited logspace',
        sender = 'antares@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        copies = [
            ('jens.krueger@frm2.tum.de', 'important'),
        ],
        subject = 'ANTARES log space runs full',
    ),
)
