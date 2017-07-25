description = 'WFM choppers'
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
    wfm_chopper_distance=device('nicos_mlz.v20.devices.distancedevice.CenteredDistanceDevice',
                                description='Distance between WFM choppers 1 and 2',
                                a='stage_wfm1',
                                b='stage_wfm2',
                                coordinates='equal',
                                ),
)
