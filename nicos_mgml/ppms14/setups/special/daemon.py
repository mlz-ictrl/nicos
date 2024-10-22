description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [
            ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
            ('admin', 'f3309476bdb36550aa8fb90ae748c9cc', 'admin'),
        ],
    ),
    OAuth = device('nicos.services.daemon.auth.oauth2.Authenticator',
        tokenurl = 'https://user.mgml.eu/o/token/',
        clientid = 'obzjsc0ybtIfz5AWnKot34mM2bcrjOWkrIa71ZMt',
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        # 'localhost' will normally bind the daemon to the loopback
        # device, therefore just clients on the same machine will be
        # able to connect !
        # '' will bind these daemon to all network interfaces in the
        # machine
        # If server is a hostname (official computer name) or an IP
        # address the daemon service will be bound the the
        # corresponding network interface.
        server = 'kfes2.troja.mff.cuni.cz:1301',
        # server = 'localhost:1301',
        authenticators = ['Auth', 'OAuth'],
        loglevel = 'info',
    ),
)
