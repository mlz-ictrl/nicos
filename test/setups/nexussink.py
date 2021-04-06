name='nexussink setup'

includes = ['stdsystem', 'scanning', 'detector']

sinklist = ['nexussink',]

sysconfig = dict(datasinks = sinklist,)

devices = dict(
    nexussink=device('nicos.nexus.nexussink.NexusSink',
        description="Sink for NeXus file writer",
        filenametemplate=['test%(year)sn%(scancounter)06d.hdf',],
        templateclass='test.nexus.TestTemplateProvider.TestTemplateProvider',
    ),
)
