Utility functions
=================

.. currentmodule:: nicos.utils

The :mod:`nicos.utils` contains a collection of general use utility classes:

.. autoclass:: AutoDefaultODict

.. autoclass:: AttrDict

.. autoclass:: BoundedOrderedDict

.. autoclass:: Device

.. autoclass:: FitterRegistry

.. autoclass:: HardwareStub

.. autoclass:: LCDict

.. autoclass:: ReaderRegistry

.. autoclass:: Repeater

.. autoclass:: lazy_property

.. autoclass: readonlydict

.. autoclass:: readonlylist

The :mod:`nicos.utils` contains a collection of general use utility functions:

.. autofunction:: allDays

.. autofunction:: bitDescription

.. autofunction:: checkSetupSpec

.. autofunction:: chunks

.. autofunction:: clamp

.. autofunction:: closeSocket

.. autofunction:: colorcode

.. autofunction:: colorize

.. autofunction:: createSubprocess

.. autofunction:: createThread

.. autofunction:: daemonize

.. autofunction:: decodeAny

.. autofunction:: disableDirectory

.. autofunction:: enableDirectory

.. autofunction:: enableDisableDirectory

.. autofunction:: enableDisableFileItem

.. autofunction:: ensureDirectory

.. autofunction:: expandTemplate

.. autofunction:: extractKeyAndIndex

.. autofunction:: findResource

.. autofunction:: fixupScript

.. autofunction:: formatDocstring

.. autofunction:: formatDuration

.. autofunction:: formatEndtime

.. autofunction:: formatException

.. autofunction:: formatExtendedFrame

.. autofunction:: formatExtendedStack

.. autofunction:: formatExtendedTraceback

.. autofunction:: formatScriptError

.. autofunction:: getPidfileName

.. autofunction:: getSysInfo

.. autofunction:: getVersions

.. autofunction:: getfqdn

.. autofunction:: importString

.. autofunction:: make_load_config

.. autofunction:: moveOutOfWay

.. autofunction:: nocolor

.. autofunction:: num_sort

.. autofunction:: parseConnectionString

.. autofunction:: parseDateString

.. autofunction:: parseDuration

.. autofunction:: parseHostPort

.. autofunction:: printTable

.. autofunction:: readFile

.. autofunction:: readFileCounter

.. autofunction:: removePidfile

.. autofunction:: resolveClasses

.. autofunction:: safeName

.. autofunction:: safeWriteFile

.. autofunction:: setuser

.. autofunction:: squeeze

.. autofunction:: syncFile

.. autofunction:: tabulated

.. autofunction:: tcpSocket

.. autofunction:: tcpSocketContext

.. autofunction:: terminalSize

.. autofunction:: timedRetryOnExcept

.. autofunction:: uniq

.. autofunction:: updateFileCounter

.. autofunction:: watchFileContent

.. autofunction:: watchFileTime

.. autofunction:: which

.. autofunction:: whyExited

.. autofunction:: writeFile

.. autofunction:: writePidfile



When adding new functions or classes to :mod:`nicos.utils`, be aware that this
module shall be kept independent from the  rest of nicos to allow early importing.
This specifcally means that you can not use NICS exceptions( :mod:`nicos.core.exceptions`),
the NICOS session (`nicos.session`) or NICOS logging functions. If you require such
functionality :mod:`nicos.core.utils` is the appropriate place.
