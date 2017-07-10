description = 'setup for the electronic logbook'
group = 'special'

# If you want to use the electronic logbook, make sure the "system" setup has
# also a cache configured.

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
        prefix = 'logbook/',
        cache = 'resedahw',
    ),
)
