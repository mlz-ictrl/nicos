# -*- coding: utf-8 -*-
"""
    nicm.errors
    ~~~~~~~~~~~

    Exception classes for usage in NICOS.
"""


class NicmError(Exception):
    category = 'Error'

class ConfigurationError(NicmError):
    category = 'Configuration error'

class UsageError(NicmError):
    category = 'Usage error'

class ProgrammingError(NicmError):
    category = 'Programming error'

class PositionError(NicmError):
    category = 'Positioning error'

class CommunicationError(NicmError):
    category = 'Communication error'

class OutofBoundsError(NicmError):
    category = 'Out of bounds'

class DeviceUndefinedError(NicmError):
    category = 'Device undefined'
