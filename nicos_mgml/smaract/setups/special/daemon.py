description = 'setup for the execution daemon'

group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        # first entry is the user name, second the hashed password, third the user level
        passwd = [
            ('user', '12dea96fec20593566ab75692c9949596833adc9', 'user'),
            ('admin', 'd04f99151f214f97b672660eb524f7577ffc4a3f', 'admin'),
        ],
    ),
    OAuth = device('nicos.services.daemon.auth.oauth2.Authenticator',
        tokenurl = 'https://user.mgml.eu/o/token/',
        clientid = 'obzjsc0ybtIfz5AWnKot34mM2bcrjOWkrIa71ZMt',
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        authenticators = ['Auth', 'OAuth'],
        loglevel = 'info',
        server = 'kfes12.troja.mff.cuni.cz',
    ),
)
