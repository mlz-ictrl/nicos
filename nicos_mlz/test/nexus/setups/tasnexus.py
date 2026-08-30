includes = ['tas', 'detector', 'reactor']

sysconfig = dict(
    datasinks = ['nxsink', ],
)

devices = dict(
    nxsink = device('nicos_mlz.nexus.NexusSink',
        templateclass = 'nicos_mlz.nexus.templates.TasTemplateProvider',
        filenametemplate = ['%(pointcounter)07d.nxs'],
        settypes = {'point'},
        detectors = ['det'],
        device_mapping = {
            'detector': 'det',
        },
    ),
)
