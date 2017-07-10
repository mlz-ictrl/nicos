description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'sans1ctrl.sans1.frm2'
)

devices = dict(
   Poller = device('nicos.services.poller.Poller',
                   alwayspoll = ['collimation', 'pressure',
                                 'astrium',
                                 'detector',
                                 'reactor', 'selector_tower',
                                 'guidehall', 'nl4a', 'memograph',
                                 'ubahn', 'outerworld',
                                ],
                   blacklist = [],
                  ),
)
