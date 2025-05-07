description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
                    # the hashing maybe 'md5' or 'sha1'
                    hashing = 'md5',
                    passwd = [('guest', '', 'guest'),
                              ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                              ('admin', '21232f297a57a5a743894a0e4a801fc3', 'admin'),
                             ],
                   ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    # 'localhost' will normally bind the daemon to the loopback
                    # device, therefore just clients on the same machine will be
                    # able to connect !
                    # '' will bind the daemon to all network interfaces in the
                    # machine
                    # If server is a hostname (official computer name) or an IP
                    # address the daemon service will be bound to the
                    # corresponding network interface.
                    server = '0.0.0.0',
                    authenticators = ['Auth'],
                    loglevel = 'info',
                   ),
)
