# This setup file configures the nicos elog.
# If you want to use the electronic logbook, make sure the "system" setup has
# also a cache configured.

description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
        prefix = 'logbook/',
        cache = 'lauectrl.laue.frm2',
    ),
)
