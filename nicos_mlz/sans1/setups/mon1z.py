#
# Ist noch als AnNA.tel device vorhanden!!! geht noch nicht!!!
# Monitor 1 z-Achse
#

description = 'Selector'

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    # mon1z = device('nicos.devices.generic.Axis',
    #     motor = 'mon1z_mot',
    #     coder = 'mon1z_enc',
    #     tacodevice = nethost + 'sel/sel/z',
    #     fmtstr = '%.2f',
    #     abslimits = (0, 500), #need to check
    # ),
    mon1_mot = device('nicos.devices.taco.motor.Motor',
        description = 'mon1z motor',
        tacodevice = '//%s/sans1/z/motor' % (nethost,),
        fmtstr = '%.2f',
        abslimits = (0, 500),  #need to check
    ),
    mon1_enc = device('nicos.devices.taco.coder.Coder',
        description = 'mon1z encoder',
        tacodevice = '//%s/sans1/z/enc' % (nethost,),
        fmtstr = '%.2f',
    ),
)
