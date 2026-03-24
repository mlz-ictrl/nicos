description = 'setup for the NICOS watchdog'
group = 'special'

watch_conditions = [
    dict(condition = 'lin1_tp_status[0] == ERROR',
         message = 'lin1_tp hardware error',
         type = 'critical',
         gracetime = 2,
         scriptaction = 'immediatestop',
         ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
                      cache = 'localhost:14869',
                      notifiers = {'default': [],
                                   'critical': []},
                      watch = watch_conditions,
                     ),
)
