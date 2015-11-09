# This setup file configures the nicos poller service.

description = 'setup for the NICOS watchdog'
group = 'special'

watchlist = [
]

notifiers = {
    'default':  [],
    'critical': [],
}

devices = dict(
    # Configure source and copy addresses to an existing address.
    # mailer   = device('devices.notifiers.Mailer',
    #                   sender = 'me@frm2.tum.de',
    #                   receivers = ['me@frm2.tum.de', 'you@frm2.tum.de'],
    #                   subject = 'NICOS Warning',
    #                  ),

    # Configure SMS receivers if wanted and registered with IT.
    # smser    = device('devices.notifiers.SMSer',
    #                   server = 'triton.admin.frm2',
    #                   receivers = [],
    #                  ),

    Watchdog = device('services.watchdog.Watchdog',
                      # use only 'localhost' if the cache is really running on
                      # the same machine, otherwise use the official computer
                      # name
                      cache = 'localhost',
                      notifiers = notifiers,
                      mailreceiverkey = 'email/receivers',
                      watch = watchlist,
                     ),
)
