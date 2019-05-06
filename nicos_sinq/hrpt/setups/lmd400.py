description = 'LMD400 detector data logger'

pvprefix = 'SQ:HRPT:lmd400:'

devices = dict (
        lmd400=device('nicos_sinq.hrpt.devices.lmd400.LMD400',
                   description='LMD400 data logger',
                   basepv=pvprefix,
                   epicstimeout=5.0,
            ),
)
