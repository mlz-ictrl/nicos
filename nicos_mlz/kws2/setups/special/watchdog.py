description = 'setup for the NICOS watchdog'
group = 'special'

watchlist = [
    dict(condition = 'ep01_t_value > 80 or ep02_t_value > 80 or ep03_t_value > 80 or '
                     'ep04_t_value > 80 or ep05_t_value > 80 or ep06_t_value > 80 or '
                     'ep07_t_value > 80 or ep08_t_value > 80 or ep09_t_value > 80 or '
                     'ep10_t_value > 80 or ep11_t_value > 80 or ep12_t_value > 80 or '
                     'ep13_t_value > 80 or ep14_t_value > 80 or ep15_t_value > 80 or '
                     'ep16_t_value > 80 or ep17_t_value > 80 or ep18_t_value > 80',
         message = 'Eight-pack temperature alarm, shutting down detector power',
         scriptaction = 'immediatestop',
         action = 'move("gedet_power", "off")',
         gracetime = 10,
         type = 'default',
    ),
    dict(condition = 'det_kwscounting and '
                     'abs(selector_speed_value - selector_speed_target) > '
                     'selector_speed_precision',
         message = 'Selector outside of target speed, count paused',
         okmessage = 'Selector back at target speed',
         scriptaction = 'pausecount',
         gracetime = 10,
         type = 'default',
    ),
    dict(condition = 'det_kwscounting and '
                     '(abs(chopper_params_value[0] - chopper_params_target[0]) > 0.1 or '
                     'abs(chopper_params_value[1] - chopper_params_target[1]) > 1)',
         message = 'Chopper outside of target frequency/phase, count paused',
         okmessage = 'Chopper back at target frequency/phase',
         scriptaction = 'pausecount',
         gracetime = 1,
         type = 'default',
    ),
    dict(condition = 'det_kwscounting and shutter_value != "open"',
         message = 'Shutter closed, count paused',
         okmessage = 'Shutter open again',
         scriptaction = 'pausecount',
         gracetime = 1,
         type = 'default',
    ),
    dict(condition = 'det_kwscounting and (sixfold_shutter_value != "open" or '
                     'nl3a_shutter_value != "open")',
         message = 'Sixfold or NL3a shutter closed, count paused',
         okmessage = 'Sixfold or NL3a shutter open again',
         scriptaction = 'pausecount',
         gracetime = 1,
         type = 'default',
    ),
    dict(condition = 'det_kwscounting and '
                     'abs(t_peltier_value - t_peltier_setpoint) > '
                     '2 * t_peltier_precision',
         message = 'Peltier temperature outside of setpoint, count paused',
         okmessage = 'Peltier temperature normal again',
         scriptaction = 'pausecount',
         gracetime = 1,
         type = 'default',
         setup = 'peltier',
    ),
    dict(condition = 'det_kwscounting and '
                     'abs(t_julabo_value - t_julabo_setpoint) > '
                     '2 * t_julabo_precision',
         message = 'Julabo temperature outside of setpoint, count paused',
         okmessage = 'Julabo temperature normal again',
         scriptaction = 'pausecount',
         gracetime = 1,
         type = 'default',
         setup = 'waterjulabo',
    ),
    dict(condition = 'det_kwscounting and (chopper1_freq_status[0] == WARN or '
                     'chopper2_freq_status[0] == WARN)',
         message = 'Chopper off, but not in parking position',
         gracetime = 10,
         type = 'default',
         setup = 'chopper',
    ),
]

includes = ['notifiers']

notifiers = {
    'default':  ['email'],
    'critical': ['email', 'smser'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watchlist,
    ),
)
