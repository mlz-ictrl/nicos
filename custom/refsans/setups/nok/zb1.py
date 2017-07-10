description = 'Slit ZB1 using beckhoff controllers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    # zb1 is at exit of NOK5b (so on its sample side)
    zb1_m    = device('nicos_mlz.refsans.beckhoff.nok.BeckhoffMotorCab1M13',
                      description = 'CAB1 controlled zb1 (M23), sample side',
                      tacodevice = '//%s/test/modbus/optic'% (nethost,),
                      address = 0x3020+7*10, # word adress
                      slope = 10000,
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (-184, -0.1),
                      userlimits = (-146.0656, -0.1),
                      lowlevel = True,
                     ),
    zb1     = device('nicos.devices.generic.Axis',
                     description = 'zb1, singleslit',
                     motor = 'zb1_m',
                     coder = 'zb1_m',
                     obs = [],
                     offset = -37.9344,
                     precision = 0.002,
                    ),
              )
