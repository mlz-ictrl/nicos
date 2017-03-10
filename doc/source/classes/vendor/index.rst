Vendor-specific device classes
==============================

These devices are implementations of the communication with devices from a
specific vendor.  There are not many such implementations in the NICOS core
because most device-specific communication is handled by TACO servers, which
present a standard interface to NICOS described :ref:`here <taco>`.

.. toctree::
   :maxdepth: 1

   caress
   ipc
   toni
   iseg
   qmesydaq
   frm2
   astrium
   lima
   simplecomm
