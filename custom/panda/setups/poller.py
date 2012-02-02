description = 'setup for the poller'
group = 'special'

includes = []

devices = dict(
    Poller = device('nicos.poller.Poller'),
)
