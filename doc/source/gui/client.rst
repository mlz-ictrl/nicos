.. _gui-client:

The GUI client class
====================

.. module:: nicos.clients.gui.client

An instance of this class is available on the GUI's main window and on every
panel object as ``self.client``.  It can be used to initiate actions in the
NICOS daemon or to query it for current state or values.

.. class:: NicosGuiClient

   **Lower level methods**

   .. automethod:: tell

      For example, to queue some code to be executed, use ``client.tell('queue',
      '', 'read()')``.  For a list of all commands, see :ref:`daemon-commands`.

   .. automethod:: ask

   .. automethod:: eval

   **Signals**

   For every :ref:`daemon event <daemon-events>`, the client emits a Qt signal
   with the same name.  For example, to bind a handler to the ``status`` event
   on a panel, use ::

      self.connect(self.client, SIGNAL('status'), self.on_client_status)

   **Higher level methods**

   .. automethod:: getDeviceList

   .. automethod:: getDeviceValue

   .. automethod:: getDeviceValuetype

   .. automethod:: getDeviceParamInfo

   .. automethod:: getDeviceParams

   .. automethod:: getDeviceParam

   .. automethod:: getCacheKey
