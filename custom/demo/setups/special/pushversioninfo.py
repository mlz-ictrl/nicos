description = 'configuration for the version updater'
group = 'special'

JENKINS_URI = ('http://resi2.office.frm2:8080/jenkins/buildByToken/'
               'buildWithParameters?job=UpdateNicosWiki')

devices = dict(
    PushVersionInfo = device('nicos.services.pushversioninfo.PushVersionInfo',
                             description = 'updates locally running version '
                             'in central wikipage',
                             update_uri = JENKINS_URI,
                             infokey = 'info',
                             cache = 'localhost:14869',
                             tokenid = 'frm2jenkins'
                            ),
)
