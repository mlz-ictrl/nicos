# -*- coding: utf-8 -*-
"""
    nicm.errors
    ~~~~~~~~~~~

    Exception classes for usage in NICOS.
"""


class NicmError(Exception):
    category = 'Error'

class ProgrammingError(NicmError):
    category = 'NICOS bug'

class ConfigurationError(NicmError):
    category = 'Configuration error'

class UsageError(NicmError):
    category = 'Usage error'

class PositionError(NicmError):
    category = 'Position error'

class MoveError(NicmError):
    category = 'Positioning error'

class LimitError(NicmError):
    category = 'Out of bounds'

class CommunicationError(NicmError):
    category = 'Communication error'
