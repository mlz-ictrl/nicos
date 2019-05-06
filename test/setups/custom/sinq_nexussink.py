name='sinq_nexussink setup'

includes = ['stdsystem', 'scanning', 'detector']

sinklist = ['nexussink',]

sysconfig = dict(datasinks = sinklist,)

devices = dict(
    nexussink=device('nicos_sinq.nexus.nexussink.NexusSink',
        description="Sink for NeXus file writer",
        filenametemplate=['test%(year)sn%(scancounter)06d.hdf',],
        templatesmodule='test.nicos_sinq.nexus.TestTemplateProvider',
        templateclass='TestTemplateProvider',
    ),
)
