# -*- coding: utf-8 -*-
"""
    nicm.commands.output
    ~~~~~~~~~~~~~~~~~~~~

    Module for output/logging user commands.
"""

from nicm import nicos

__commands__ = [
    'printdebug', 'printinfo', 'printwarning', 'printerror', 'printexception',
]


def printdebug(*msgs, **kwds):
    nicos.log.debug(*msgs, **kwds)

def printinfo(*msgs, **kwds):
    nicos.log.info(*msgs, **kwds)

def printwarning(*msgs, **kwds):
    nicos.log.warning(*msgs, **kwds)

def printerror(*msgs):
    nicos.log.error(*msgs)

def printexception(*msgs):
    nicos.log.exception(*msgs)
