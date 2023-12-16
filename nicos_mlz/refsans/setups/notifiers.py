description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    # Configure source and copy addresses to an existing address.
    email = device('nicos.devices.notifiers.Mailer',
        mailserver = 'mailhost.frm2.tum.de',
        sender = 'refsans@frm2.tum.de',
        copies = [
            ('matthias.pomm@hereon.de', 'all'),  # gets all messages
            #('matthias.pomm@web.de', 'all'),  # gets all messages
            #('refsans@hereon.de', 'important'),
            #('refsans@hereon.de', 'all'),
        ],
        subject = 'NICOS',
    ),

    # Configure SMS receivers if wanted and registered with IT.
    smser = device('nicos.devices.notifiers.SMSer',
        server = 'triton.admin.frm2.tum.de',
        receivers = [
            #'015123629866',
            '01799553828',
            ],
    ),
)
