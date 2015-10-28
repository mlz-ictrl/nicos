# This setup file configures the nicos poller service.

description = 'setup for the NICOS watchdog'
group = 'special'

watchlist = [
]

includes = ['notifiers']

notifiers = {
    'default':  [],
    'critical': [],
}

devices = dict(
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
