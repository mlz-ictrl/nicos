description = 'common definitions for all instruments using the "frm2" setups'
group = 'configdata'

# Names of all the available CCR boxes.
all_ccrs = [f'ccr{i}' for i in [10, 11, 12] + list(range(14, 26))]
# Names of all the available CCI inserts (3He and dilution).
all_ccis = ['cci3he01', 'cci3he02', 'cci3he03',
            'cci3he10', 'cci3he11', 'cci3he12', 'ccidu01', 'ccidu02']
# Names of all the available RSC (Newport rotation stages).
all_rscs = ['rsc01', 'rsc02', 'rsc03', 'rsc10', 'rsc11', 'rsc12']
