description = 'setup for the poller'

group = 'special'

includes = []

sysconfig = dict(
    cache = 'pandasrv'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    autosetup = False,
                    poll = ['lakeshore', 'detector', 'befilter', 'cryo1',
                            'cryo3', 'cryo4', 'cryo5', 'magnet75', '7T5',
                            'ccr11', 'ccr16', 'panda', 'sat'],
                    alwayspoll = [],
                    neverpoll = [],
                    #~ blacklist=['sB', 'ss1', 'ss2'],
                    ),
)
