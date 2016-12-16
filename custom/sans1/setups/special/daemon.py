description = 'setup for the execution daemon'
group = 'special'

devices = dict(
    UserDB = device('frm2.proposaldb.Authenticator'),
    Auth   = device('services.daemon.auth.ListAuthenticator',
                    hashing = 'md5',
                    # first entry is the user name, second the hashed password, third the user level
                    passwd = [
                              ('guest', '', 'guest'),
                              ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                              ('admin', 'ec326b6858b88a51ff1605197d664add', 'admin'),
                              ('andreas', 'da5121879fff54b08b69ec54d9ac2bf6', 'admin'),
                              ('andre', '1b2bc04a135d959e8da04733e24195da', 'admin'),
                              ('sebastian', '6c79a7389f572813edfe5fc873e099ce', 'admin'),
                              ('sbusch', 'b71e7f18a043b020b4935f6694a918cf', 'admin'),
                              ('edv', 'cb50179ebd60c94a29770c652a848765', 'admin'),
                              ],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'sans1ctrl.sans1.frm2',
                    authenticators = ['UserDB', 'Auth'],
                    loglevel = 'debug',
                   ),
)
