description = 'Vaccum sensors and temperature control'

devices = dict(
    vacuum=device(
        'nicos_ess.estia.devices.pfeiffer.PfeifferTPG261',
        description='Pfeiffer TPG 261 vacuum gauge controller',
        hostport='192.168.1.254:4002',
        fmtstr='%.2E',
    ),
)
