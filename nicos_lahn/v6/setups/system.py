description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='RNP',
    experiment='Exp',
    datasinks=[
        'conssink',
        'filesink',
        'daemonsink',
        'livesink',
        'nxsink'],
    # 'rawsink', 'nxsink'],
    # notifiers = [],  # ['email'],
)

modules = ['nicos.commands.standard', 'nicos_lahn.commands.secoplist']

includes = [
    #    'notifiers',
]

devices = dict(
    RNP=device('nicos.devices.instrument.Instrument',
               description='Polarized Neutron Reflectometer',
               instrument='RNP',
               responsible='Marina Tortarolo <tortarol@tandar.cnea.gov.ar>',
               website='https://www.argentina.gob.ar/laboratorio-argentino-de-haces-de-neutrones/instrumento-de-reflectometria-de-neutrones',
               operators=['Laboratorio Argentino de Haces de Neutrones'],
               facility='LAHN',
               ),
    Sample=device('nicos.devices.sample.Sample',
                  description='The currently used sample',
                  ),

    # Configure dataroot here (usually /data).
    Exp=device('nicos.devices.experiment.Experiment',
               description='experiment object',
               dataroot='/mnt/nfs/rnp/data',
               sendmail=True,
               serviceexp='service',
               sample='Sample',
               forcescandata=True,
               ),
    filesink=device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink=device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink=device('nicos.devices.datasinks.DaemonSink'),
    livesink=device('nicos.devices.datasinks.LiveViewSink'),
    #rawsink = device ('nicos.devices.datasinks.RawImageSink'),
    nxsink=device('nicos.nexus.NexusSink',
                  templateclass='nicos_lahn.v6.nexus.nexus_templates.RNPTemplateProvider',
                  filenametemplate=['%(proposal)s_%(scancounter)08d.hdf'],
                  ),
    Space=device('nicos.devices.generic.FreeSpace',
                 description='The amount of free space for storing data',
                 path='/mnt/nfs',
                 warnlimits=(5., None),
                 minfree=5,
                 ),
    LogSpace=device('nicos.devices.generic.FreeSpace',
                    description='Space on log drive',
                    path=None,
                    warnlimits=(.5, None),
                    minfree=0.5,
                    visibility=('devlist',),
                    ),
)
