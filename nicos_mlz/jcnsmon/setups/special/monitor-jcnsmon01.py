description = 'setup for the status monitor'
group = 'special'

##################################
#### define devices here #########
##################################

## 8T Magnet ccm8v ##
ccm8v = Block('ccm8v - 8T MAGNET', [
    BlockRow(Field(name='Field', dev='se/B_ccm8v',unit='T'),
             Field(name='Hall', dev='se/ccm8v_Bhall', unit='T'),
                 Field(name='P_sample', dev='se/ccm8v_psample',unit='mbar'),
            ),
    '---',
    BlockRow(Field(name='T_VTI', dev='se/T_ccm8v_vti'),
             Field(name='VTI heat', dev='se/ccm8v_vti_heater'),
             Field(name='VTI NV', dev='se/ccm8v_vti_nv'),
             Field(name='P_VTI', dev='se/ccm8v_pvti'),
            ),
    '---',
    BlockRow(Field(name='LT-Stick', dev='se/T_ccm8v_stick'),
             Field(name='LT-heat', dev='se/ccm8v_stick_heater'),
                 Field(name='HT-Stick', dev='se/T_ccm8v_htstick'),
             Field(name='HT-heat', dev='se/ccm8v_htstick_heater'),
            ),
    '---',
    BlockRow(Field(name='Coils', dev='se/ccm8v_Tmag'),
             Field(name='Dewar', dev='se/ccm8v_pdewar', unit=' '),
             Field(name='Coldhead', dev='se/ccm8v_Tcoldhead'),
             Field(name='P_iso', dev='se/ccm8v_piso',unit='mbar'),
            ),
    BlockRow(Field(name='LHe', dev='se/ccm8v_LHe'),
             Field(name='LN2', dev='se/ccm8v_LN2'),
            ),

    BlockRow(Field(plot='p_ccm8v', name='LHe', key='se/ccm8v_LHe/value',
                plotwindow=36000, width=40, height=30, fontsize=20),
                Field(plot='p_ccm8v', name='LN2', key='se/ccm8v_LN2/value')
            ),
])

## HTS 3T Magnet ##
ccm3a_1 = Block('ccm3a - HTS 3T', [
        BlockRow(Field(name='B', dev='se/B_ccm3a_readback', unit='T')
                ),
        BlockRow(Field(name='T1', dev='se/ccm3a_T1', unit='K'),
                 Field(name='T2', dev='se/ccm3a_T2', unit='K'),
                 Field(name='T3', dev='se/ccm3a_TA', unit='K'),
                 Field(name='T4', dev='se/ccm3a_TB', unit='K'),
                ),
        BlockRow(Field(plot='ccm3a_plot', name='T1', key='se/ccm3a_T1/value',
                       plotwindow=3600, width=40, height=30, fontsize=20),
                  Field(plot='ccm3a_plot', name='T2',key='se/ccm3a_T2/value'),
                  Field(plot='ccm3a_plot', name='T3',key='se/ccm3a_TA/value'),
                  Field(plot='ccm3a_plot', name='T4',key='se/ccm3a_TB/value'),
                ),
])

## SPHERES CRYO PLOT ##
cct6_1 = Block('cct6 - SPHERES CRYO', [
        BlockRow(Field(name='T tube',   dev='se/cct6_T_tube',     unit='K'),
                 Field(name='T sample', dev='se/cct6_T_sample',   unit='K'),
                 Field(name='T sample 2', dev='se/cct6_sample2',  unit='K'),
                ),
        '---',
        BlockRow(Field(name='tube SP',  dev='se/cct6_T_tube/setpoint',   unit='K'),
                 Field(name='sample SP',dev='se/cct6_setpoint', unit='K'),
                 Field(name='pressure', dev='se/cct6_c_pressure', unit='mbar'),
                ),
        BlockRow(Field(name='heater tube',   dev='se/cct6_T_tube/heateroutput',   unit='%'),
                 Field(name='heater sample', dev='se/cct6_T_sample/heateroutput', unit='%'),
                ),
        BlockRow(Field(plot='temp_cct6', name='T sample', key='se/cct6_T_sample/value',
                       plotwindow=3600, width=30, height=30, fontsize=60),
                 Field(plot='temp_cct6', name='T tube', key='se/cct6_T_tube/value'),
                 Field(plot='temp_cct6', name='T sample2', key='se/cct6_T_c_pressure/value'),
                ),
])

##################################
#### define layout on monitor ####
##################################
layout1 = [Row(Column(ccm8v), Column(cct6_1,ccm3a_1))]
layout2 = [Row(Column(ccm8v), Column(cct6_1), Column(ccm3a_1))]
layout3 = [Row(Column(cct6_1))]


##################################
#### general settings ############
##################################
devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = '',
        loglevel = 'info',
        cache = 'jcnsmon.jcns.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 16,
        padding = 2,
        layout = layout2,
        expectmaster = False,
    ))
