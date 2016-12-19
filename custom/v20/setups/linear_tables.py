description = 'Setup with two permanently available linear tables via CARESS.'

servername = 'EXV20'
nameservice = '192.168.1.254'

devices = dict(
    lin1=device('devices.vendor.caress.Motor',
                description='Huber linear table 400mm',
                fmtstr='%.2f',
                unit='mm',
                coderoffset=0,
                abslimits=(0, 400),
                nameserver='%s' % (nameservice,),
                objname='%s' % (servername),
                config='LIN1 500 nist222dh1787.hmi.de:/st222.caress_object CopleyStepnet '
                       '17 2000 CopleyStepnet 17 2000 0',
                ),
    lin2=device('devices.vendor.caress.Motor',
                description='Huber linear table 100mm',
                fmtstr='%.2f',
                unit='mm',
                coderoffset=0,
                abslimits=(0, 100),
                nameserver='%s' % (nameservice,),
                objname='%s' % (servername),
                config='LIN2 500 nist222dh1787.hmi.de:/st222.caress_object CopleyStepnet '
                       '18 4000 CopleyStepnet 18 4000 0',
                ),
)
