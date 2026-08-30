
includes = ['detector', 'reactor', 'cryo']

sysconfig = dict(
    datasinks = ['nxsink', ],
)

devices = dict(
    nxsink = device('nicos_mlz.nexus.NexusSink',
        templateclass = 'nicos_mlz.nexus.template.MLZTemplateProvider',
        filenametemplate = ['%(pointcounter)07d.nxs'],
        settypes = {'point'},
        detectors = ['det'],
        device_mapping = {
            'detector': 'det',
        },
    ),
)
