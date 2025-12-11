.. _gui-cmdlets:

Cmdlets
=======

Introduction
------------

.. module:: nicos.clients.gui.cmdlets

.. autoclass:: Cmdlet()

Existing Cmdlets
----------------

.. module:: nicos.clients.gui.cmdlets

.. class:: Move()

  :func:`move <nicos.commands.device.move>`

  :func:`maw <nicos.commands.device.maw>`

   .. figure:: cmdlets/move_cmdlet.png
      :align: center

.. class:: WaitFor()

  :func:`waitfor <nicos.commands.device.waitfor>`

   .. figure:: cmdlets/waitfor_cmdlet.png
      :align: center

  :func:`waitfor_stable <nicos.commands.device.waitfor_stable>`

   .. figure:: cmdlets/waitfor_stable_cmdlet.png
      :align: center

.. class:: Count()

   :py:func:`count <nicos.commands.measure.count>`

   .. figure:: cmdlets/count_cmdlet.png
      :align: center

.. class:: Scan()

   :py:func:`scan <nicos.commands.scan.scan>`

   :py:func:`contscan <nicos.commands.scan.contscan>`

   .. figure:: cmdlets/scan_cmdlet.png
      :align: center

.. class:: CScan()

   :py:func:`cscan <nicos.commands.scan.cscan>`

   .. figure:: cmdlets/cscan_cmdlet.png
      :align: center

.. class:: Center()

   :py:func:`center <nicos.commands.analyze.center>`

   .. figure:: cmdlets/center_cmdlet.png
      :align: center

.. class:: TimeScan()

   :py:func:`timescan <nicos.commands.scan.timescan>`

   .. figure:: cmdlets/timescan_cmdlet.png
      :align: center

.. class:: ContScan()

   :py:func:`contscan <nicos.commands.scan.contscan>`

   .. figure:: cmdlets/contscan_cmdlet.png
      :align: center

.. class:: Sleep()

   :py:func:`sleep <nicos.commands.basic.sleep>`

   .. figure:: cmdlets/sleep_cmdlet.png
      :align: center

.. class:: Configure()

  :py:func:`set <nicos.commands.device.set>`

   .. figure:: cmdlets/configure_cmdlet.png
      :align: center

.. class:: NewSample()

   :py:func:`NewSample <nicos.commands.sample.NewSample>`

   .. figure:: cmdlets/newsample_cmdlet.png
      :align: center

.. class:: nicos.clients.gui.cmdlets.tomo.Tomo()

   :py:func:`tomo <nicos.commands.imaging.tomo>`

   .. figure:: cmdlets/tomo_cmdlet.png
      :align: center

.. class:: nicos.clients.gui.cmdlets.qscan.QScan()

   :py:func:`qscan <nicos.commands.tas.qscan>`

   .. figure:: cmdlets/qscan_cmdlet.png
      :align: center
