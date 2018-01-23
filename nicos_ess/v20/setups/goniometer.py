description = 'Goniometer'

servername = 'EXV20'
nameservice = '192.168.1.254'

loadblock='''read=always,async
'''

devices = dict(
    omega=device('nicos.devices.vendor.caress.Motor',
                 description='Omega',
                 fmtstr='%.2f',
                 unit='deg',
                 coderoffset=0,
                 abslimits=(0, 360),
                 nameserver=nameservice,
                 objname=servername,
                 config='OMEGA 500 nist222dh1787.hmi.de:/st222.caress_object CopleyStepnet '
                        '20 144000 CopleyStepnet 20 144000 0',
                 loadblock=loadblock,
                 ),
    phi=device('nicos.devices.vendor.caress.Motor',
               description='Phi',
               fmtstr='%.2f',
               unit='deg',
               coderoffset=0,
               abslimits=(-360, 360),
               nameserver=nameservice,
               objname=servername,
               config='PHI 500 nist222dh1787.hmi.de:/st222.caress_object CopleyStepnet '
                      '21 144000 CopleyStepnet 21 144000 0',
               loadblock=loadblock,
               ),
    chi=device('nicos.devices.vendor.caress.Motor',
               description='Chi',
               fmtstr='%.2f',
               unit='deg',
               coderoffset=0,
               abslimits=(-15, 15),
               nameserver=nameservice,
               objname=servername,
               config='CHI 500 nist222dh1787.hmi.de:/st222.caress_object CopleyStepnet '
                      '22 4000 CopleyStepnet 22 4000 0',
               loadblock=loadblock,
               ),
)

