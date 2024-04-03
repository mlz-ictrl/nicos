Vendor-specific device classes
==============================

These devices are implementations of the communication with devices from a
specific vendor.  There are not many such implementations in the NICOS core
because most device-specific communication is handled by :ref:`TANGO <tango>`
servers or :ref:`EPICS <epics>` IOC's, which present a standard interface to NICOS.

.. toctree::
   :maxdepth: 1

   caress
   ipc
   qmesydaq
   astrium
   lima
   cascade
