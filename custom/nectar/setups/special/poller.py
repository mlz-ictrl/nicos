description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'nectarhw.nectar.frm2'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    alwayspoll = [], # setups that should be polled regardless if loaded
                    neverpoll = [],  # setups that should not be polled even if loaded
                    blacklist = ['ccd'],  # DEVICES that should never be polled
                                     # (usually detectors or devices that have problems
                                     # with concurrent access from processes)
                   ),
)
