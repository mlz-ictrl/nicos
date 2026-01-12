description = 'Translation stage A setup'

group = 'optional'

servername = 'EXV6'
nameservice = '172.16.1.1'

loadblock_TRANSA = '''motion_usefloat=yes
motion_displayformat=%0.2f
motion_display=18
loadoffset=yes
'''

devices = dict(
    trans_a=device(
        'nicos.devices.vendor.caress.Motor',
        description='translation',
        fmtstr='%.2f',
        unit='mm',
        abslimits=(
            0,
            100),
        nameserver='%s' %
        nameservice,
        objname='%s' %
        servername,
        config='TRANS_A	500	172.16.1.3:/st222.caress_object	CopleyStepnet	4	-2000	CopleyStepnet	4			-2000	0',
        loadblock=loadblock_TRANSA,
    ),
)
