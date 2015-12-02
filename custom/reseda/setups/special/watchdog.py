description = 'setup for the NICOS watchdog'
group = 'special'



watchlist = [
    dict(condition = 'sel_value < 6000',
         message = 'Problem with selector. Value below 6000rpm',
         gracetime = 2,
         ),

]

includes = ['notifiers', ]

devices = dict(
    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'resedahw',
                      notifiers = {'default': ['email']},
                      watch = watchlist,
                      mailreceiverkey = 'email/receivers',
                     ),
)
