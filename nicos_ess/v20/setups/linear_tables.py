description = 'Linear tables'

pvprefix = 'HZB-V20:MC-MCU-01:'

servername = 'EXV20'
nameservice = '192.168.1.254'
loadblock = '''start=never,async
stop=never,async
read=always,async
motion_TBG=0.1
motion_TBK=0.01
motion_usefloat=true
motion_autodelete=false
motion_display=36
motion_displayformat=%0.3f
motion_retries=1
loadoffset=yes
'''

devices = dict(
    lin1 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'Huber linear table 400mm via EPICS',
        unit = 'mm',
        fmtstr = '%.2f',
        abslimits = (0, 400),
        epicstimeout = 3.0,
        precision = 0.1,
        motorpv = pvprefix + 'm12',
        errormsgpv = pvprefix + 'm12-MsgTxt',
        errorbitpv = pvprefix + 'm12-Err',
        reseterrorpv = pvprefix + 'm12-ErrRst'
    ),

    lin2 = device('nicos.devices.vendor.caress.Motor',
        description = 'Huber linear table 100mm via CARESS',
        fmtstr = '%.2f',
        unit = 'mm',
        coderoffset = 0,
        abslimits = (0, 100),
        nameserver = nameservice,
        objname = servername,
        config = 'LIN2 500 nist222dh1787.hmi.de:/st222.caress_object '
                 'CopleyStepnet 18 4000 CopleyStepnet 18 4000 0',
        loadblock = loadblock,
    ),

#    lin3 = device('nicos.devices.vendor.caress.Motor',
#        description = 'Huber linear table 100mm via CARESS',
#        fmtstr = '%.2f',
#        unit = 'mm',
#        coderoffset = 0,
#        abslimits = (0, 100),
#        nameserver = nameservice,
#        objname = servername,
#        config = 'LIN3 500 nist222dh1787.hmi.de:/st222.caress_object '
#                 'CopleyStepnet 19 400000 CopleyStepnet 19 400000 0',
#        loadblock = loadblock,
#    ),

    height1 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'height1 via EPICS',
        unit = 'mm',
        fmtstr = '%.2f',
        abslimits = (0, 40),
        epicstimeout = 3.0,
        precision = 0.1,
        motorpv = pvprefix + 'm9',
        errormsgpv = pvprefix + 'm9-MsgTxt',
        errorbitpv = pvprefix + 'm9-Err',
        reseterrorpv = pvprefix + 'm9-ErrRst'
    ),
)

