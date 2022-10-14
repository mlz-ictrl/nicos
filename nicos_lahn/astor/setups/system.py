description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    # Adapt this name to your instrument's name (also below).
    instrument='ASTOR',
    experiment='Exp',
    datasinks=['conssink', 'filesink', 'daemonsink', 'livesink', 'fitsimgsink'],
    # notifiers = [],  # ['email'],
)

modules = ['nicos.commands.standard', 'nicos.commands.imaging']

includes = [
    #    'notifiers',
]

devices = dict(
    ASTOR=device('nicos.devices.instrument.Instrument',
                 description='Advanced System of Tomography and Radiography',
                 instrument='ASTOR',
                 responsible='Dr. Nahuel A. Vega" <nahuelvega@cnea.gob.ar>',
                 website='http://www.lahn.cnea.gov.ar/index.php/instrumentacion/tomografo',
                 operators=['Laboratorio Argentino de Haces de Neutrones'],
                 facility='LAHN',
                 ),
    Sample=device('nicos.devices.sample.Sample',
                  description='The currently used sample',
                  ),

    # Configure dataroot here (usually /data).
    Exp=device('nicos.devices.experiment.Experiment',
               description='experiment object',
               dataroot='/mnt/nfs/astor/data',
               sendmail=True,
               serviceexp='service',
               sample='Sample',
               ),
    filesink=device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink=device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink=device('nicos.devices.datasinks.DaemonSink'),
    livesink=device('nicos.devices.datasinks.LiveViewSink'),
    fitsimgsink=device('nicos.devices.datasinks.FITSImageSink'),
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
