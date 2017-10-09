description = 'setup for the poller'
group = 'special'

includes = []

sysconfig = dict(
    cache = 'pumahw.puma.frm2'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        autosetup = True,
        # setups for which all devices are polled
        # poll = ['lakeshore', 'detector', 'befilter'],
        # setups which are always polled
        alwayspoll = [],
        # setups which are never polled
        neverpoll = ['motorbus1', 'motorbus2', 'motorbus3', 'motorbus4',
                     'motorbus5', 'motorbus6', 'motorbus6a', 'motorbus7',
                     'motorbus6', 'motorbus9', 'motorbus10', 'motorbus11',],
    ),
)
