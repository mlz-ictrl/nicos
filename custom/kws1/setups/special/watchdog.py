# This setup file configures the nicos watchdog service.

description = 'setup for the NICOS watchdog'
group = 'special'

watchlist = [
    dict(condition = 'det_kwscounting and det_mode != "realtime" and '
                     'det_mode != "realtime_external" and '
                     'abs(selector_speed_value - selector_speed_target) > '
                     'selector_speed_precision',
         message = 'Selector outside of target speed, count paused',
         scriptaction = 'pausecount',
         gracetime = 1,
         type = 'default',
    ),
    dict(condition = 'det_kwscounting and det_mode != "realtime" and '
                     'det_mode != "realtime_external" and '
                     'shutter_value != "open"',
         message = 'Shutter closed, count paused',
         scriptaction = 'pausecount',
         gracetime = 1,
         type = 'default',
    ),
    dict(condition = 'det_kwscounting and det_mode != "realtime" and '
                     'det_mode != "realtime_external" and '
                     'sixfold_shutter_value != "open"',
         message = 'Sixfold shutter closed, count paused',
         scriptaction = 'pausecount',
         gracetime = 1,
         type = 'default',
    ),
]

includes = ['notifiers']

notifiers = {
    'default':  ['email'],
    'critical': ['email', 'smser'],
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
