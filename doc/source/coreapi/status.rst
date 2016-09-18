Status values
=============

.. module:: nicos.core.status

The :mod:`nicos.core.status` module defines the status constants that are used
as the first item of the tuple that `.Device.status` returns.  The whole
`status` module is re-exported in :mod:`nicos.core`.

.. data:: OK

   The device is in a ready or idle state with no errors.

.. data:: BUSY

   The device is in a busy state (moving or waiting for completion).

.. data:: NOTREACHED

   The device has not reached its target/setpoint.

.. data:: ERROR

   The device is in an error state.

.. data:: UNKNOWN

   The state of the device is not known.

.. data:: statuses

   A dictionary mapping these status values, which are integers, to their
   lowercased name (i.e., ``statuses[ERROR] == 'error'``).
