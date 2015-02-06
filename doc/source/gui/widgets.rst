.. _gui-widgets:

Display widgets
===============

Introduction
------------

For easy programming of graphical interfaces, NICOS provides a couple of
Qt widgets that can display and edit information about NICOS devices or
device parameters.

The same widgets are used in the GUI client as well as in the status monitor,
therefore they are located in the ``nicos.guisupport`` package.

Existing widgets are:

``ValueDisplay`` (in nicos.guisupport.display)
   Displays the name and value of either a device or any other value from
   the cache.

``TrendPlot`` (in nicos.guisupport.plots)
   Displays a time series of one or more devices/cache values.

``ValueLed`` and ``StatusLed`` (in nicos.guisupport.led)
   Displays a boolean value or a device status as a stylized LED.

``DeviceValueEdit`` and ``DeviceParamEdit`` (in nicos.guisupport.typedvalue)
   Displays a widget (or a number of widgets) suitable for editing the value
   of a device or parameter.  For example, a normal edit box (with validators)
   is used for floating values, while combo box is used for values with a
   fixed number of choices.


Widget interface
----------------

This section describes the interface of the NicosWidget class, which methods
and attributes you can use and override when you implement your own widget.

.. module:: nicos.clients.gui.widget

.. class:: NicosWidget


   **Class attributes to be overridden**

   .. attribute:: designer_description

      A string with a short description of the widget; this is used for the Qt
      designer.  If this is not set, the widget will not be included in the
      designer.

   .. attribute:: designer_icon

      Resource name of the icon to use for the designer.  If this is not set, Qt
      will use a default icon.

   .. attribute:: properties

      This is a dictionary that specifies the properties of the widget that
      should be settable from the Qt designer.  The keys are property names, and
      the values must be instances of :class:`PropDef` (see the example below).

      For each entry, a Qt property is created that can be used from the code
      like a normal Python property.

   **Instance attributes**

   .. attribute:: props

      A dictionary with the current values of the properties defined with
      :attr:`properties`.

   .. attribute:: _client

      The daemon client object (see :ref:`gui-client`) if the widget is used
      from a GUI (as opposed to e.g. the NICOS monitor), otherwise ``None``.

   **Methods to override**

   .. method:: initUi()

      Here you should create the user interface of the widget.

   .. method:: propertyUpdated(pname, value)

      This method is called whenever a property defined in :attr:`properties` is
      updated.  *pname* is the property name, *value* is the new value (which is
      already set in :attr:`props`).

      You should call the base class implementation if you override this.

   .. method:: registerKeys()

      See :meth:`registerDevice` and :meth:`registerKey`.

   .. method:: on_devValueChange(dev, value, strvalue, unitvalue, expired)

   .. method:: on_devStatusChange(dev, code, status, expired)

   .. method:: on_devMetaChange(dev, fmtstr, unit, fixed)

   **Methods to use**

   .. method:: registerDevice(dev, valueindex=-1, unit='', fmtstr='')

   .. method:: registerKey(valuekey, statuskey='', valueindex=-1, unit='', fmtstr='')


An example widget::

   # TBW.
