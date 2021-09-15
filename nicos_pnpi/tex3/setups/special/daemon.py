description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'sha1',
        # for the meaning of these entries see
        # https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/daemon/#nicos.services.daemon.auth.list.Authenticator
        passwd = [
            ('guest', '', 'guest'),
            # The entries for these password hashes are generated from randomized
            # passwords and not reproduceable, please don't forget to create new
            # ones.
            ('user', '524c2a0a7472a49032bbc78aba99746ef9e4f235', 'user'),
            ('admin', '524c2a0a7472a49032bbc78aba99746ef9e4f235', 'admin'),
        ],
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
        server = 'localhost',
        authenticators = ['Auth'],
        loglevel = 'info',
    ),
)
