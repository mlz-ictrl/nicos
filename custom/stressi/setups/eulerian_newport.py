description = 'STRESS-SPEC setup with Newport Eulerian cradle'

group = 'basic'

includes = ['aliases', 'system', 'mux', 'monochromator', 'detector',
	    'sampletable', 'primaryslit', 'slits', 'reactor']

excludes = ['eulerian_huber', 'eulerian_tensile', 'robot']

sysconfig = dict(
    datasinks = ['caresssink'],
)

servername = 'VME'

nameservice = 'stressictrl'

devices = dict(
    chis_n = device('devices.vendor.caress.Motor',
                    description = 'HWB CHIN',
                    fmtstr = '%.2f',
                    unit = 'deg',
                    # coderoffset = 3319.25,
                    coderoffset = 0,
                    abslimits = (-5, 90),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    # TODO Check the right settings
                    # config = 'CHIN 114 11 0x00f1e000 3 20480 8000 800 2 24 50 '
                    #          '-1 0 1 5000 1 10 0 0 0',
                    config = 'CHIN 115 11 0x00f1e000 3 500 500 50 1 0 0 '
                             '0 0 1 5000 1 10 0 0 0',
                   ),
    phis_n = device('devices.vendor.caress.Motor',
                    description = 'HWB PHIN',
                    fmtstr = '%.2f',
                    unit = 'deg',
                    coderoffset = 2048,
                    abslimits = (-720, 720),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    # config = 'PHIN 114 11 0x00f1c000 2 50 200 20 2 24 50 1 0 '
                    #          '1 5000 1 10 0 0 0',
                    config = 'PHIN 115 11 0x00f1c000 2 50 200 20 2 24 50 1 0 '
                             '1 5000 1 10 0 0 0',
                   ),
    # phis = device('devices.vendor.caress.Motor',
    #               description = 'HWB PHIS',
    #               fmtstr = '%.2f',
    #               unit = 'deg',
    #               coderoffset = 0,
    #               abslimits = (-720, 720),
    #               nameserver = '%s' % (nameservice,),
    #               objname = '%s' % (servername),
    #               config = 'PHIS 115 11 0x00f1d000 2 100 200 20 1 0 0 0 0 '
    #                        '1 5000 1 10 0 0 0',
    #              ),
)

alias_config = {
    'chis': {'chis_n': 200,},
    'phis': {'phis_n': 200,},
}
