# -*- coding: utf-8 -*-

description = 'Virtual selector area setup'
group = 'lowlevel'
display_order = 22

res_presets = configdata('config_resolution.RESOLUTION_PRESETS')

devices = dict(
    resolution      = device('nicos_mlz.kws3.devices.resolution.Resolution',
                             description = 'select resolution presets',
                             blockingmove = False,
                             moveables = ['sel_ap2_x_left', 'sel_ap2_x_right',
                                          'sel_ap2_y_lower', 'sel_ap2_y_upper',
                                          'det_x', 'det_y', 'det_z'],
                             mapping = {k: list(v['ap']) +  [v['det_x'], v['det_y'], v['det_z']]
                                        for (k, v) in res_presets.items()},
                             fallback = 'unknown',
                             precision = [0.1, 0.1, 0.1, 0.1, 0.01, 0.01, 0.01],
                             presets = res_presets,
                            ),

    sel_ap1         = device('nicos.devices.generic.TwoAxisSlit',
                             description = 'aperture before selector',
                             fmtstr = '%.3f %.3f',
                             horizontal = 'sel_ap1_width',
                             vertical = 'sel_ap1_height',
                            ),
    sel_ap1_width   = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'aperture before selector horizontal opening',
                             lowlevel = True,
                            ),
    sel_ap1_height  = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'aperture before selector vertical opening',
                             lowlevel = True,
                            ),
    sel_ap2         = device('nicos.devices.generic.Slit',
                             description = 'selector jj-xray aperture',
                             left = 'sel_ap2_x_left',
                             right = 'sel_ap2_x_right',
                             bottom = 'sel_ap2_y_lower',
                             top = 'sel_ap2_y_upper',
                            ),
    sel_ap2_x_left  = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'selector jj-xray aperture left',
                             lowlevel = True,
                            ),
    sel_ap2_x_right = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'selector jj-xray aperture right',
                             lowlevel = True,
                            ),
    sel_ap2_y_upper = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'selector jj-xray aperture upper',
                             lowlevel = True,
                            ),
    sel_ap2_y_lower = device('nicos_mlz.kws1.devices.virtual.Standin',
                             description = 'selector jj-xray aperture lower',
                             lowlevel = True,
                            ),
)

extended = dict(
    poller_cache_reader = ['det_x', 'det_y', 'det_z'],
)
