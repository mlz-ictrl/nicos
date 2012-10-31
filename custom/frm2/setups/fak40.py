description = 'FRM-II FAK40 information (cooling water system)'

nethost = 'tacodb.taco.frm2'

devices = dict(
        FAK40_Cap = device('nicos.taco.AnalogInput',
                       tacodevice = '//%s/frm2/fak40/capacity' % (nethost, ),
                       description = 'The capacity of the cooling water system',
                       pollinterval = 60,
                       maxage = 120,
                      ),
        FAK40_Press = device('nicos.taco.AnalogInput',
                       tacodevice = '//%s/frm2/fak40/pressure' % (nethost, ),
                       description = 'The pressure inside the cooling water system',
                       pollinterval = 60,
                       maxage = 120,
                      ),
)

startupcode = """
"""
