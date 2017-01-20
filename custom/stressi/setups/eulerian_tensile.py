description = 'STRESS-SPEC setup with Tensile rigg Eulerian cradle'

group = 'basic'

includes = ['system', 'mux', 'monochromator', 'detector', 'sampletable',
            'primaryslit', 'slits', 'reactor']

excludes = ['eulerian_huber', 'eulerian_newport', 'robot']

sysconfig = dict(
    datasinks = ['caresssink'],
)

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

devices = dict(
    chis_t = device('devices.vendor.caress.Motor',
                    description = 'Tensile CHIS',
                    fmtstr = '%.2f',
                    unit = 'deg',
                    coderoffset = 0,
                    abslimits = (85, 185),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    config = 'CHIS 115 11 0x00f1e000 3 350 500 50 1 0 0 0 0 1 '
                             '5000 1 10 0 0 0',
                    lowlevel = True,
                   ),
    phis_t = device('devices.vendor.caress.Motor',
                    description = 'Tensile PHIS',
                    fmtstr = '%.2f',
                    unit = 'deg',
                    coderoffset = 0,
                    abslimits = (-720, 720),
                    nameserver = '%s' % (nameservice,),
                    objname = '%s' % (servername),
                    # TODO: check which is the correct setup
                    config = 'PHIS 115 11 0x00f1f000 3 30 80 8 1 0 0 0 0 1 '
                             '5000 1 10 0 0 0',
                    # config = 'PHIS 115 11 0x00f1d000 4 30 20 2 1 0 0 0 0 1 '
                    #          '5000 1 10 0 0 0',
                    lowlevel = True,
                   ),
)

alias_config = {
    'chis': {'chis_t': 200,},
    'phis': {'phis_t': 200,},
}
