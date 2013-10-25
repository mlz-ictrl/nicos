description = 'setup for the NICOS watchdog'
group = 'special'



watchlist = [
    dict(condition = 'sel_value < 6000',
         message = 'Problem with selector. Value below 6000rpm',
         gracetime = 2,
         ),

]


devices = dict(

    email    = device('devices.notifiers.Mailer',
                      sender = 'Nicolas.Martin@frm2.tum.de',
                      receivers = ['awischol@frm2.tum.de',],
                      subject = 'Warning',
                     ),

    Watchdog = device('services.watchdog.Watchdog',
                      cache = 'resedahw',
                      notifiers = {'default': ['email']},
                      watch = watchlist,
                      mailreceiverkey = 'email/receivers',
                     ),
)
