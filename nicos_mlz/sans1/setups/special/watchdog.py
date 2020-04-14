description = 'setup for the NICOS watchdog'
group = 'special'

# The entries in this list are dictionaries. Possible keys:
#
# 'setup' -- setup that must be loaded (default '' to mean all setups)
# 'condition' -- condition for warning (a Python expression where cache keys
#    can be used: t_value stands for t/value etc.
# 'gracetime' -- time in sec allowed for the condition to be true without
#    emitting a warning (default 5 sec)
# 'message' -- warning message to display
# 'priority' -- 1 or 2, where 2 is more severe (default 1)
# 'action' -- code to execute if condition is true (default no code is executed)

watchlist = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'critical',
         gracetime = 30,
    ),
    dict(condition = '(sixfold_value == "closed" or nl4a_value == "closed") '
                     'and reactorpower_value > 19',
         message = 'NL4a or sixfold shutter closed',
         type = 'critical',
    ),
    dict(condition = 't_in_memograph_value > 20',
         message = 'Cooling water inlet temperature exceeds 20 C, check FAK40 and SANS-1 memograph!',
         #type = 'critical',
         type = None,
         gracetime = 30,
    ),
    dict(condition = 'ReactorPower_value < 19',
         message = 'Reactor power is below 19 MW!',
         #type = 'critical',
         type = None,
         gracetime = 120,
    ),
    dict(condition = 'ccmsans_T5_value > 4.5',
         message = 'Magnet T5 > 4.5 K, check for possible quench of magnet!',
         #type = 'critical',
         type = None,
         setup = 'ccmsans',
         gracetime = 5,
    ),
    dict(condition = 'coll_tube_value > 1',
         message = 'Pressure within collimation tube above 1 mbar!\nCheck if pump is running.',
         #type = 'critical',
         type = None,
         gracetime = 30,
    ),
    dict(condition = 'coll_nose_value > 1',
         message = 'Pressure within collimation nose above 1 mbar!\nCheck if pump is running.',
         #type = 'critical',
         type = None,
         gracetime = 30,
    ),
    dict(condition = 'det_nose_value > 0.5',
         message = 'Pressure within detector nose above 0.5 mbar!\nCheck if pump is running.',
         #type = 'critical',
         type = None,
         gracetime = 30,
    ),
    dict(condition = 'det_tube_value > 0.5',
         message = 'Pressure within detector tube above 0.5 mbar!\nCheck if pump is running.',
         #type = 'critical',
         type = None,
         gracetime = 30,
    ),
    dict(condition = 'p_diff_wut_value > 0.5',
         message = 'Differential pressure at filter above 0.5 bar!\nClean Filter.',
         #type = 'critical',
         type = None,
         gracetime = 60,
    ),
    dict(condition = 'det1_hv_ax_value < 1000',
         message = 'Detector Voltage down for more than 15 min!\nCheck high voltage.',
         #type = 'critical',
         type = None,
         gracetime = 900,
    ),
    dict(condition = 'chopper_ch2_phase_value < 4.7 or chopper_ch2_phase_value > 4.9',
         message = 'Chopper 2 lost parking phase position!',
         #type = 'critical',
         type = None,
         setup = 'not tisane',
         gracetime = 5,
         action = 'move(chopper_ch2_parkingpos, 4.8)',
    ),
    dict(condition = 'chopper_ch1_phase_value < 16.1 or chopper_ch1_phase_value > 16.3',
         message = 'Chopper 1 lost parking phase position!',
         #type = 'critical',
         type = None,
         setup = 'not tisane',
         gracetime = 5,
         action = 'move(chopper_ch1_parkingpos, 16.2)',
    ),
    dict(condition = 'selector_rpm_value > 30000',
         message = 'selector rpm above 30000.\nPlease check Selector hardware!!!',
         #type = 'critical',
         type = None,
         gracetime = 30,
    ),
    dict(condition = 'chopper_waterflow_value < 3',
         message = 'Low Waterflow for chopper!!!\nCheck filter and pressure knob!',
         #type = 'critical',
         type = None,
         gracetime = 30,
    ),
]


# The Watchdog device has two lists of notifiers, one for priority 1 and
# one for priority 2.

includes = ['notifiers']

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
                      cache = 'sans1ctrl.sans1.frm2:14869',
                      #notifiers = {'default': ['info'], 'critical': ['email']},
                      notifiers = {},
                      watch = watchlist,
                      #mailreceiverkey = 'email/receivers',
                     ),
)
