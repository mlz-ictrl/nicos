description = 'Vacuum sensors of collimation tube'

includes = ['system']

excludes = ['collimation']

group = 'lowlevel'  # should not be visible to users

tangohost = 'tango://sans1hw.sans1.frm2:10000'

devices = dict(
    col_2a_m = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
        description = 'CollimatorMotor 2a',
        # IP-adresse: 172.16.17.7
        tangodevice = '%s/coll/col-2m/modbus' % (tangohost, ),
        address = 0x4020+1*10,
        slope = 200*4,  # FULL steps per turn * turns per mm
        microsteps = 8,
        unit = 'mm',
        refpos = -8.,
        abslimits = (-400, 600),
        # hw_disencfltr = 'enabled',
        autozero = 20,
        autopower =1,
    ),
    # at = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'Attenuator',
    #     # IP-adresse: 172.16.17.1
    #     tangodevice='%s/coll/ng-pol/modbus'% (tangohost, ),
    #     address = 0x4020+0*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -23.0,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, OPEN=0, x10=117, x100=234, x1000=351 ),
    # ),
    # ng_pol = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'Neutronguide polariser',
    #     # IP-adresse: 172.16.17.1
    #     tangodevice='%s/coll/ng-pol/modbus'% (tangohost, ),
    #     address = 0x4020+1*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -4.5,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, POL1=117, POL2=234, LASER=351 ),
    # ),
    # col_20a = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 20a',
    #     # IP-adresse: 172.16.17.2
    #     tangodevice='%s/coll/col-20m/modbus'% (tangohost, ),
    #     address = 0x4020+0*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -5.39,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # col_20b = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 20b',
    #     # IP-adresse: 172.16.17.2
    #     tangodevice='%s/coll/col-20m/modbus'% (tangohost, ),
    #     address = 0x4020+1*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -5.28,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # bg1 = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'Background slit1 motor',
    #     # IP-adresse: 172.16.17.3
    #     tangodevice='%s/coll/col-16m/modbus'% (tangohost, ),
    #     address = 0x4020+0*10,
    #     slope = 200*0.16, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -28.85,
    #     abslimits = (-40, 300),
    #     mapping = {'P1':0, 'P2':90, 'P3':180, 'P4':270,
    #     '50mm':0, 'OPEN':90, '20mm':180, '42mm':270 },
    # ),
    # col_16a = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 16a',
    #     # IP-adresse: 172.16.17.3
    #     tangodevice='%s/coll/col-16m/modbus'% (tangohost, ),
    #     address = 0x4020+1*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -4.29,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # col_16b = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 16b',
    #     # IP-adresse: 172.16.17.3
    #     tangodevice='%s/coll/col-16m/modbus'% (tangohost, ),
    #     address = 0x4020+2*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -2.31,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # col_12a = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 12a',
    #     # IP-adresse: 172.16.17.4
    #     tangodevice='%s/coll/col-12m/modbus'% (tangohost, ),
    #     address = 0x4020+0*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -1.7,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # col_12b = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 12b',
    #     # IP-adresse: 172.16.17.4
    #     tangodevice='%s/coll/col-12m/modbus'% (tangohost, ),
    #     address = 0x4020+1*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -9.999, #XXX: Angabe fehlt in Doku !!!
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # bg2 = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'Background slit2',
    #     # IP-adresse: 172.16.17.5
    #     tangodevice='%s/coll/col-8m/modbus'% (tangohost, ),
    #     address = 0x4020+0*10,
    #     slope = 200*0.16, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -1.5,
    #     abslimits = (-40, 300),
    #     mapping = {'P1':0, 'P2':90, 'P3':180, 'P4':270,
    #     '28mm':0, '20mm':90, '12mm':180, 'OPEN':270 },
    # ),
    # col_8a = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 8a',
    #     # IP-adresse: 172.16.17.5
    #     tangodevice='%s/coll/col-8m/modbus'% (tangohost, ),
    #     address = 0x4020+1*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -3.88,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # col_8b = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 8b',
    #     # IP-adresse: 172.16.17.5
    #     tangodevice='%s/coll/col-8m/modbus'% (tangohost, ),
    #     address = 0x4020+2*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -4.13,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # col_4a = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 4a',
    #     # IP-adresse: 172.16.17.6
    #     tangodevice='%s/coll/col-4m/modbus'% (tangohost, ),
    #     address = 0x4020+1*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -9.37,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # col_4b = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 4b',
    #     # IP-adresse: 172.16.17.6
    #     tangodevice='%s/coll/col-4m/modbus'% (tangohost, ),
    #     address = 0x4020+2*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -9.35,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # col_sa1 = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'attenuation slits',
    #     # IP-adresse: 172.16.17.7
    #     tangodevice='%s/coll/col-2m/modbus'% (tangohost, ),
    #     address = 0x4020+0*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -34.7,
    #     abslimits = (-40, 300),
    #     mapping = {'P1':0, 'P2':70, 'P3':140, 'P4':210,
    #     '50x50':0, '30mm':70, '20mm':140, '10mm':210 },
    # ),
    # col_2b = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliMotorAllParams',
    #     description = 'CollimatorMotor 2b',
    #     # IP-adresse: 172.16.17.7
    #     tangodevice='%s/coll/col-2m/modbus'% (tangohost, ),
    #     address = 0x4020+2*10,
    #     slope = 200*4, # FULL steps per turn * turns per mm
    #     microsteps = 8,
    #     unit = 'mm',
    #     refpos = -9.,
    #     abslimits = (-400, 600),
    #     mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
    # ),
    # pump devices of 172.17.17.10 are at modbus-tangodevice //sans1srv.sans.frm2/sans1/coll/pump
)
