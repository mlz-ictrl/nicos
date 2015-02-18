description = 'setup for the poller'

group = 'special'

includes = []

sysconfig = dict(
    cache = 'phys.panda.frm2'
)

devices = dict(
    Poller = device('services.poller.Poller',
                    loglevel = 'info',
                    autosetup = True,
                    #~ poll = ['lakeshore', 'detector', 'befilter', 'cryo1',
                            #~ 'cryo3', 'cryo4', 'cryo5', 'magnet75', '7T5',
                            #~ 'ccr11', 'ccr16', 'panda', 'sat', 'saph','water'],
                    alwayspoll = ['water'],
                    neverpoll = ['blenden'],
                    blacklist = ['ss1', 'ss2'],
                    ),
)
