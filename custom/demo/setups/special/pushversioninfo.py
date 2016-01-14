description = 'configuration for the version updater'
group = 'special'

JENKINS_URI = ('http://resi2.office.frm2:8080/jenkins/buildByToken/'
               'buildWithParameters?token=TestAuth&job=UpdateNicosWiki&')

devices = dict(
    PushVersionInfo = device('services.pushversioninfo.PushVersionInfo',
                             description = 'updates locally running version '
                             'in central wikipage',
                             update_uri = JENKINS_URI,
                             infokey = 'info',
                             cache = 'localhost:14869',
                            ),
)
