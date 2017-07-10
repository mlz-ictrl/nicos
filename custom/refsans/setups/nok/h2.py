description = 'Slit H2 using Beckhoff controllers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf'
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'
# according to docu: '_Anhang_A_REFSANS_Pumpstand.pdf'
devices = dict(
    # according to '_2013-04-05 Anhang A V0.6.pdf'
    # beckhoff is at 'horizontalblende.refsans.frm2' / 172.25.18.109
    # hs_center is the offset of the slit-center to the beam
    # hs_width is the opening of the slit
    h2_center = device('nicos_mlz.refsans.beckhoff.nok.BeckhoffMotorHSlit',
                       description = 'Horizontal slit system: offset of the slit-center to the beam',
                       tacodevice = '//%s/test/modbus/h2'% (nethost,),
                       address = 0x3020+0*10, # word adress
                       slope = 1000,
                       unit = 'mm',
                       # acording to docu:
                       abslimits = (-69.5, 69.5),
                      ),
    h2_width = device('nicos_mlz.refsans.beckhoff.nok.BeckhoffMotorHSlit',
                      description = 'Horizontal slit system: opening of the slit',
                      tacodevice = '//%s/test/modbus/h2'% (nethost,),
                      address = 0x3020+1*10, # word adress
                      slope = 1000,
                      unit = 'mm',
                      # acording to docu:
                      abslimits = (0.05, 69.5),
                     ),
              )
