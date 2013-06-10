description = 'setup for the NICOS watchdog'
group = 'special'



watchlist = [
    dict(condition = 'length_value < 100',
         message = 'Length is messed up',
         priority = 2),

##    dict(condition = '',
##         message = '',
##         gracetime = 5),
]


devices = dict(

    email    = device('devices.notifiers.Mailer',
                      sender = 'awischol@frm2.tum.de',
                      receivers = ['awischol@frm2.tum.de', 'awischol@frm2.tum.de'],
                      subject = 'Warning',
                     ),

    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'localhost:14869',
                      notifiers_1 = ['email'],
                      notifiers_2 = ['email'],
                      watch = watchlist,
                     ),
)
