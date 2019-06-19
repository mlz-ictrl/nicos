description = 'Goniometer'

pvprefix = 'HZB-V20:MC-MCU-01:'

servername = 'EXV20'
nameservice = '192.168.1.254'
loadblock='''read=always,async
'''

devices = dict(
    alpha = device('nicos.devices.vendor.caress.Motor',
        description = 'Alpha via CARESS',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (-25, 25),
        nameserver = nameservice,
        objname = servername,
        config = 'ALPHA 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 17 3777 CopleyStepnet 17 3777 0',
        loadblock = loadblock,
    ),

    omega=device('nicos.devices.vendor.caress.Motor',
                 description='Omega',
                 fmtstr='%.2f',
                 unit='deg',
                 coderoffset=0,
                 abslimits=(-360, 360),
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

    omega2 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'omega2 via EPICS',
        unit = 'mm',
        fmtstr = '%.2f',
        epicstimeout = 3.0,
        precision = 0.1,
        motorpv = pvprefix + 'm10',
        errormsgpv = pvprefix + 'm10-MsgTxt',
        errorbitpv = pvprefix + 'm10-Err',
        reseterrorpv = pvprefix + 'm10-ErrRst'
    ),

    beta = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'beta via EPICS',
        unit = 'mm',
        fmtstr = '%.2f',
        abslimits = (-35, 35),
        epicstimeout = 3.0,
        precision = 0.1,
        motorpv = pvprefix + 'm11',
        errormsgpv = pvprefix + 'm11-MsgTxt',
        errorbitpv = pvprefix + 'm11-Err',
        reseterrorpv = pvprefix + 'm11-ErrRst'
    ),
)
