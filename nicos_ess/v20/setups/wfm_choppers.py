description = 'WFM Chopper cascade'
servername = 'EXV20'
nameservice = '192.168.1.254'

devices = dict(
    stage_wfm1=device('nicos.devices.vendor.caress.Motor',
                      description='Linear stage for WFM chopper 1 (upstream)',
                      fmtstr='%.2f',
                      unit='mm',
                      coderoffset=0,
                      abslimits=(-180, -34),
                      nameserver='%s' % (nameservice,),
                      objname='%s' % (servername),
                      config='MTUS 500 nist222dh1787.hmi.de:/st222.caress_object CopleyStepnet '
                             '1 -7272.727273 BeckhoffKL5001 BK5120/63/32/0/0 824 4151568',
                      lowlevel=True,
                      ),
    stage_wfm2=device('nicos.devices.vendor.caress.Motor',
                      description='Linear stage for WFM chopper 2 (downstream)',
                      fmtstr='%.2f',
                      unit='mm',
                      coderoffset=0,
                      abslimits=(34, 180),
                      nameserver='%s' % (nameservice,),
                      objname='%s' % (servername),
                      config='MTDS 500 nist222dh1787.hmi.de:/st222.caress_object CopleyStepnet '
                             '7 7272.727273 BeckhoffKL5001 BK5120/63/32/4/0 -819 4154609',
                      lowlevel=True,
                      ),
    wfm_chopper_distance=device('nicos_ess.v20.devices.distancedevice.CenteredDistanceDevice',
                                description='Distance between WFM choppers 1 and 2',
                                a='stage_wfm1',
                                b='stage_wfm2',
                                coordinates='equal',
                                ),

    wfm_choppers_ioc=device('nicos_ess.v20.devices.rest_service.RestServiceClientDevice',
                            host='172.17.0.2:8080',
                            service='wfm_chopper_cascade',
                            description='WFM Chopper Cascade IOC',
                            lowlevel=True,
                            requires={'user': 'admin'}),

    wfm_c1=device('nicos_ess.v20.devices.jcns_choppers.JCNSChopper',
                  unit='Deg',
                  pvprefix='V20:C01:',
                  description='WFM Chopper 1'),

    wfm_c2=device('nicos_ess.v20.devices.jcns_choppers.JCNSChopper',
                  unit='Deg',
                  pvprefix='V20:C02:',
                  description='WFM Chopper 2'),

    wfm_c3=device('nicos_ess.v20.devices.jcns_choppers.JCNSChopper',
                  unit='Deg',
                  pvprefix='V20:C03:',
                  description='WFM Chopper 3'),

    wfm_c4=device('nicos_ess.v20.devices.jcns_choppers.JCNSChopper',
                  unit='Deg',
                  pvprefix='V20:C04:',
                  description='WFM Chopper 4')
)
