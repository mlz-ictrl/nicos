description = 'Email and SMS notifiers'

group = 'lowlevel'

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      description = 'Email notifier',
                      sender = 'michael.schulz@frm2.tum.de',
                      copies = [('michael.schulz@frm2.tum.de', 'important'),
                                ('alerts.sw.zea2@fz-juelich.de', 'important'),
                               ],
                      subject = 'ANTARES',
                      lowlevel = True,
                     ),
    warning    = device('devices.notifiers.Mailer',
                        description = 'Watchdog email notifier',
                        sender = 'michael.schulz@frm2.tum.de',
                        copies = [('michael.schulz@frm2.tum.de', 'all')],
                        subject = 'ANTARES',
                        lowlevel = True,
                       ),
    smser    = device('devices.notifiers.SMSer',
                      description = 'SMS notifier',
                      #receivers = ['015121100909'],
                      receivers = [],
                      server = 'triton.admin.frm2',
                      lowlevel = True,
                     ),
)
