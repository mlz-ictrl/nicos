# This setup file configures the nicos daemon service.

description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    # to authenticate against the UserOffice, needs the "propdb" parameter
    # set on the Experiment object
    UserDB = device('nicos_mlz.frm2.proposaldb.Authenticator'),

    # fixed list of users:
    # first entry is the user name, second the hashed password, third the user
    # level
    # The user level are 'guest, 'user', and 'admin', ascending ordered in
    # respect to the rights
    # The entries for the password hashes are generated from randomized
    # passwords and not reproduceable, please don't forget to create new ones:
    # start python
    # >>> import hashlib
    # >>> hashlib.md5('password').hexdigest()
    # or
    # >>> hashlib.sha1('password').hexdigest()
    # depending on the hashing algorithm
    Auth   = device('nicos.services.daemon.auth.ListAuthenticator',
                    # the hashing maybe 'md5' or 'sha1'
                    hashing = 'md5',
                    passwd = [('guest', '', 'guest'),
                              ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                              ('admin', '04ec0deed0abb157dab3031b26b3db23', 'admin'),
                             ],
                   ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
                    # 'localhost' will normally bind the daemon to the loopback
                    # device, therefore just clients on the same machine will be
                    # able to connect !
                    # '' will bind the daemon to all network interfaces in the
                    # machine
                    # If server is a hostname (official computer name) or an IP
                    # address the daemon service will be bound the the
                    # corresponding network interface.
                    server = '',
                    authenticators = ['Auth'], # and/or 'UserDB'
                    loglevel = 'info',
                   ),
)
