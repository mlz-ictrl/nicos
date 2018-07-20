description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'resedactrl.reseda.frm2',
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        autosetup = True,
        alwayspoll = [],
        neverpoll = [],
        blacklist = ['scandet',
#                     'cbox_0a_reg_amp',
#                     'cbox_0b_reg_amp'
#                     'cbox_1_reg_amp',# 'cbox_1_coil_amp', 'cbox_1_fg_amp',
                    ]
    ),
)
