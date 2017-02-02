# -*- coding: utf-8 -*-

description = "Virtual polarizer motor setup"
group = "lowlevel"

devices = dict(
    pol_y    = device("kws1.virtual.Standin",
                      description = "polarizer y-table",
                     ),
    pol_tilt = device("kws1.virtual.Standin",
                      description = "polarizer tilt",
                     ),
)
