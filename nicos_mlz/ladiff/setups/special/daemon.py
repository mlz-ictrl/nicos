description = 'setup for the daemon'
group = 'special'

devices = dict(
    UserDBAuth = device('nicos_mlz.devices.ghost.Authenticator',
         description = 'FRM II user office authentication',
         instrument = 'LaDiff',
         ghosthost = configdata('ghost.ghosthost'),
         aliases = {
            'robertg': ('robert.georgii@frm2.tum.de', 'admin'),
         },
         loglevel = 'info',
    ),
    LDAPAuth = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = [
            'ldap://ladiffsrv.ladiff.frm2.tum.de',
        ],
        bindmethod = 'tls_before_bind',
        userbasedn = 'ou=People,dc=ladiff,dc=frm2,dc=tum,dc=de',
        groupbasedn = 'ou=Group,dc=ladiff,dc=frm2,dc=tum,dc=de',
        grouproles = {
            'ladiff': 'admin',
        },
    ),
    LDAPAuthBU = device('nicos.services.daemon.auth.ldap.Authenticator',
        uri = [
            'ldap://phaidra.admin.frm2.tum.de',
            'ldap://ariadne.admin.frm2.tum.de',
            'ldap://sarpedon.admin.frm2.tum.de',
            'ldap://minos.admin.frm2.tum.de',
        ],
        bindmethod = 'tls_before_bind',
        userbasedn = 'ou=People,dc=frm2,dc=tum,dc=de',
        groupbasedn = 'ou=Group,dc=frm2,dc=tum,dc=de',
        grouproles = {
            'ladiff': 'admin',
            'ictrl': 'admin',
            'se': 'user',
        }
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = 'ctrl.ladiff.frm2.tum.de',
        loglevel = 'info',
        authenticators = ['UserDBAuth', 'LDAPAuth', 'LDAPAuthBU',],
    ),
)
