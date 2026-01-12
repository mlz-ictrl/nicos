description = 'Off Specular Analysator setup'

group = 'lowlevel'

servername = 'EXV6'
nameservice = '172.16.1.1'

excludes = ['analysator']

loadblock_ROTA = '''motion_usefloat=yes
motion_displayformat=%0.2f
motion_display=17
loadoffset=yes
'''

devices = dict(
    rot_anoff=device('nicos.devices.vendor.caress.Motor',
                     description='rotation',
                     fmtstr='%.2f',
                     abslimits=(-50, 50),
                     unit='grades',
                     nameserver='%s' % nameservice,
                     objname='%s' % servername,
                     config='ROT_A	500	172.16.1.3:/st222.caress_object	CopleyStepnet	3	-2000	CopleyStepnet	3			-2000	0',
                     loadblock=loadblock_ROTA,
                     ),
)
