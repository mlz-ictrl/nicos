Electronic logbook
==================

:ref:`elog` in NICOS handles
:meth:`various events <nicos.core.sessions.Session.elogEvent>`
sent from different NICOS components, via dedicated
:class:`handler <nicos.services.elog.handler.Handler>` interfaces.

Handler interface
-----------------

The handler interface has for each of the events a method named
``handler_eventname``, i.e. the ``'setup'`` event is handled by the
:func:`handle_setup <nicos.services.elog.handler.Handler.handle_setup>`
method.

.. autoclass:: nicos.services.elog.handler.Handler
   :members:

   .. automethod:: handle_attachment
   .. automethod:: handle_detectors
   .. automethod:: handle_directory
   .. automethod:: handle_entry
   .. automethod:: handle_environment
   .. automethod:: handle_hidden
   .. automethod:: handle_image
   .. automethod:: handle_message
   .. automethod:: handle_newexperiment
   .. automethod:: handle_offset
   .. automethod:: handle_remark
   .. automethod:: handle_sample
   .. automethod:: handle_scanbegin
   .. automethod:: handle_scanend
   .. automethod:: handle_scriptbegin
   .. automethod:: handle_scriptend
   .. automethod:: handle_setup
