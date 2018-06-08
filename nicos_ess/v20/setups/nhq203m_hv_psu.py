description = 'NHQ 203M High Voltage Power Supply'
pvprefix = 'HZB-V20:NHQ203M:'

devices = dict(
    nhq1 = device('nicos_ess.devices.epics.supply.IsegNHQChannel',
         description = 'NHQ 203M Channel 1',
         pvprefix = pvprefix,
         channel = 1,
    ),

    nhq2 = device('nicos_ess.devices.epics.supply.IsegNHQChannel',
         description = 'NHQ 203M Channel 2',
         pvprefix = pvprefix,
         channel = 2,
    ),

    nhq1_current = device('nicos_ess.devices.epics.base.EpicsReadableEss',
         description = 'Actual output current',
         readpv = pvprefix + 'Curr1_rbv',
         unit = 'mA',
         fmtstr = '%.1f',
    ),

    nhq2_current = device('nicos_ess.devices.epics.base.EpicsReadableEss',
         description = 'Actual output current',
         readpv = pvprefix + 'Curr2_rbv',
         unit = 'mA',
         fmtstr = '%.1f',
    ),

)

