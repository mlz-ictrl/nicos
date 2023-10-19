description = 'tisane setup for SANS1'

group = 'basic'

modules = ['nicos_mlz.sans1.commands.tisane']

includes = ['collimation', 'detector', 'sample_table', 'det1',
            'pressure', 'selector_tower', 'memograph',
            'manual', 'guidehall', 'outerworld', 'pressure_filter',
            'col_slit', 'nl4a',
            'tisane_relais', 'tisane_multifg',  # for setfg and tcount
            # 'frequency',
            'tisane_det',
            ]

excludes = ['sans1']
