description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      description = 'E-Mail notifier',
                      sender = 'dns@frm2.tum.de',
                      copies = [('y.su@fz-juelich.de', 'all'),
                                ('k.nemkovskiy@fz-juelich.de', 'all'),
                                ('l.fleischhauer-fuss@fz-juelich.de', 'important'),
                                ('alerts.sw.zea2@fz-juelich.de', 'important'),
                               ],
                      subject = '[NICOS] DNS',
                     ),

    smser    = device('devices.notifiers.SMSer',
                      description = 'SMS notifier',
                      server = 'triton.admin.frm2',
                     ),
)
