description = 'setup for the status monitor'
group = 'special'

##################################
#### define devices here #########
##################################

## 8T Magnet ccm8v ##
ccm8v = Block('ccm8v - 8T magnet', [
    BlockRow(Field(name='Field', dev='se/B_ccm8v'),
             Field(name='Hall', dev='se/ccm8v_Bhall')),
    '---',
    BlockRow(Field(name='VTI', dev='se/T_ccm8v_vti'),
             Field(name='VTI heat', dev='se/ccm8v_vti_heater'),
             Field(name='VTI NV', dev='se/ccm8v_vti_nv')),
    BlockRow(Field(name='LT-Stick', dev='se/T_ccm8v_stick'),
             Field(name='LT-Stick heat', dev='se/ccm8v_stick_heater')),
    BlockRow(Field(name='HT-Stick', dev='se/T_ccm8v_htstick'),
             Field(name='HT-Stick heat', dev='se/ccm8v_htstick_heater')),
    '---',
    BlockRow(Field(name='Coils', dev='se/ccm8v_Tmag'),
             Field(name='Dewar', dev='se/ccm8v_pdewar', unit=' '),
             Field(name='Coldhead', dev='se/ccm8v_Tcoldhead')),
    BlockRow(Field(name='LHe', dev='se/ccm8v_LHe'),
             Field(name='LN2', dev='se/ccm8v_LN2')),
])

## HTS 3T Magnet ##
ccm3a_1 = Block('ccm3a - HTS 3T', [
        BlockRow(Field(name='B', dev='se/B_ccm3a_readback', unit='T')),
        BlockRow(Field(name='T1', dev='se/ccm3a_T1', unit='K'),
                 Field(name='T2', dev='se/ccm3a_T2', unit='K')),
        BlockRow(Field(name='T3', dev='se/ccm3a_TA', unit='K'),
                 Field(name='T4', dev='se/ccm3a_TB', unit='K')
                 )
])

## SPHERES CRYO PLOT ##
cct6_1 = Block('cct6 - SPHERES CRYO', [
        BlockRow(Field(name='pressure', dev='se/cct6_pressure', units='mbar'),
                 Field(name='T tube', dev='se/cct6_T_tube', unit='K'),
                 Field(name='T_sample', dev='se/cct6_T_sample', units='K')
                ),
#        BlockRow(Field(plot='temp', name='T sample', key='se/jlc22_T_sample/value', plotwindow=3600, width=30, height=20),
#                 Field(plot='temp', name='T tube', key='se/jlc22_T_tube/value')),
])

##################################
#### define layout on monitor ####
##################################
layout = [Row(Column(ccm8v), Column(cct6_1,ccm3a_1))]


##################################
#### general settings ############
##################################
devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'h',
        loglevel = 'info',
        cache = 'jcnsmon.jcns.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 30,
        padding = 15,
        layout = layout,
        expectmaster = False,
    ),
)
