description = 'setup for the NICOS watchdog'
group = 'special'

watchlist = [
    dict(
        condition = '(sixfold_value == "closed" or nl5_value == "closed") '
        'and reactorpower_value > 19.1',
        message = 'NL5 or sixfold shutter closed',
        type = 'critical',
    ),
    dict(
        condition = 'sel_value < 6000',
        message = 'Problem with selector. Value below 6000rpm',
        gracetime = 2,
    ),
]

includes = ['notifiers',]

devices = dict(
    Watchdog = device('services.watchdog.Watchdog',
        cache = 'resedahw2.reseda.frm2',
        notifiers = {'default': ['email']},
        watch = watchlist,
        mailreceiverkey = 'email/receivers',
    ),
)
