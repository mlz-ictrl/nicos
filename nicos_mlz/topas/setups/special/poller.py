description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'phys.topas.frm2',
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = [
        ],
        neverpoll = [],
        blacklist = [],  # DEVICES that should never be polled
        # (usually detectors or devices that have problems
        # with concurrent access from processes)
    ),
)
