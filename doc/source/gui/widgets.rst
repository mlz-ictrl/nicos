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

:class:`.ValueDisplay` (in nicos.guisupport.display)
   Displays the name and value of either a device or any other value from
   the cache, with extended features like coloring for status.

:class:`.ValueLabel` (in nicos.guisupport.display)
   A very simple label that displays a single value without coloring

:class:`.PictureDisplay` (in nicos.guisupport.display)
   Displays a picture file, with automatic checking for updates.

:class:`.TrendPlot` (in nicos.guisupport.plots)
   Displays a time series of one or more devices/cache values.

:class:`.ValueLed`, :class:`.StatusLed`, and :class:`.ClickableOutputLed` (in nicos.guisupport.led)
   Display a boolean value or a device status as a stylized LED.

:class:`.DeviceValueEdit` and :class:`.DeviceParamEdit` (in nicos.guisupport.typedvalue)
   Displays a widget (or a number of widgets) suitable for editing the value
   of a device or parameter.  For example, a normal edit box (with validators)
   is used for floating values, while combo box is used for values with a
   fixed number of choices.

All widgets are provided in the Qt designer when starting it :ref:`in the
correct way <gui-designer>`.

.. _widget_sizes:

Widget size
-----------

The size of a widget will be configured in terms of characters.  This helps the
user to get a feeling what will be the size of the widget.  The size of the a
character depends not only on the font size it also depends on the font type.

As the unit for the widget sizes will be taken the width of the character '0'
(Zero) of the valuefont.


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


.. todo::

   An example widget


Existing widget classes
-----------------------

.. module:: nicos.guisupport.display

.. class:: ValueDisplay

   .. figure:: valuedisplay.png
      :align: center

   A widget that displays a value from the cache.  It consists of two labels,
   one for the value name and one for the actual value.  Foreground and
   background colors of both labels are used to display additional information,
   such as the status of a device.

   It has the following properties (that can be set as Python properties and
   from within the Qt designer):

   .. attribute:: dev

      A NICOS device name.  If set, display the value of this device
      (``dev/value``) and also look at other keys such as ``dev/status`` to
      display other information.

   .. attribute:: key

      This specifies the key to display.  If :attr:`dev` is set, this is
      ``dev/value`` by default.

   .. attribute:: statuskey

      This specifies the key to use for displaying the status (color of the
      value).  If :attr:`dev` is set, this is ``dev/status`` by default.

   .. attribute:: name

      String to display as the name of the value.  By default this is the
      :attr:`dev` property if set.

   .. attribute:: unit

      Unit to display in the name label.  If :attr:`dev` is set, this is taken
      from the ``dev/unit`` key.

   .. attribute:: item

      Item index of the value to display.  Used for values with multiple items,
      such as tuples or lists.

   .. attribute:: format

      Format string to use for displaying the value.  If :attr:`dev` is set,
      this is taken from the ``dev/fmtstr`` key.

   .. attribute:: maxlen

      Maximum string length to display, in characters.

   .. attribute:: width

      Width of the widget, in characters.  If zero, the widget expands to fill
      the available space.

   .. attribute:: istext

      If true (not the default), display the value with a proportional font.

   .. attribute:: showName

      If true (the default), show the name label.

   .. attribute:: showStatus

      If true (the default), show the status (if possible) by coloring the value
      label's text.

   .. attribute:: showExpiration

      If true (the default), show expiration of the value by displaying "n/a"
      instead; otherwise, only the label's coloring is changed.

   .. attribute:: horizontal

      If true (not the default), display name and value next to each other
      horizontally.


.. class:: ValueLabel

   .. figure:: valuelabel.png
      :align: center

   A single label that displays a value from the cache without any styling.

   Properties:

   .. attribute:: key

      This specifies the key to display.  If it should be a device value, use
      ``dev/value``.

   There is a helper method:

   .. method:: setFormatCallback(callback)

      Set a callback that will be used to format the raw value into a string.
      By default this is just ``str``.


.. class:: PictureDisplay

   .. figure:: picturedisplay.png
      :align: center

   A widget that displays a picture in the status monitor. The picture is
   updated in intervals of 'refresh' seconds.

   Properties:

   .. attribute:: filepath

      The path to the picture to be displayed in the widget.  This can be
      absolute or relative to the NICOS root.

   .. attribute:: refresh

      The time between refreshes in seconds.  The longest it will take
      until any changes in the given picture are displayed.
      If no refresh (or 0) is provided, the picture won't be updated at all.
      Default value: 0.

   .. attribute:: height

      Height of the plot widget in characters.

   .. attribute:: width

      Width of the plot widget in characters.


.. module:: nicos.guisupport.plots

.. class:: TrendPlot

   .. figure:: trendplot.png
      :align: center

   Displays time series of one or more values.

   The plot has basic mouse controls for zooming and panning.

   Properties:

   .. attribute:: devices

      List of devices or cache keys that the plot should display.

      For devices, use device name.  For keys, use cache key with "." or "/"
      separator, e.g. ``T.heaterpower``.  To access items of a sequence, use
      subscript notation, e.g. ``T.userlimits[0]``.

   .. attribute:: names

      Names for the plot curves.  By default the device names or keys from
      :attr:`devices` are used.

   .. attribute:: plotwindow

      The range of time in seconds that should be represented by the plot.

   .. attribute:: plotinterval

      The minimum time in seconds between two points that should be plotted.

   .. attribute:: height

      Height of the plot widget in characters.

   .. attribute:: width

      Width of the plot widget in characters.


.. module:: nicos.guisupport.led

.. class:: ValueLed

   .. figure:: valueled.png
      :align: center

   An LED like image that shows if the value is either true (nonzero) or equals a
   set goal value.

   .. attribute:: dev

      Specify NICOS device name whose value is displayed.

   .. attribute:: key

      As an alternative to :attr:`dev`, specify a cache key that is displayed.

   .. attribute:: goal

      If nonempty, specifies a Python expression (such as ``1`` or ``'open'``).
      The LED is green if the value equals this expression, else red.

      If empty, the LED is green if the value is true (nonzero), else red.


.. class:: StatusLed

   .. figure:: statusled.png
      :align: center

   An LED like image that shows a device status constant:

   * green = OK
   * orange = WARN
   * yellow = BUSY
   * red = ERROR

   .. attribute:: dev

      Specify NICOS device name whose status is displayed.

   .. attribute:: key

      As an alternative to :attr:`dev`, specify a cache key that contains the
      status to display.


.. class:: ClickableOutputLed

   .. figure:: clickableoutputled.png
      :align: center

   An LED like image that shows its device's state and changes it on click.
   The LED then changes its color to orange until the value is updated in
   the cache.

   .. attribute:: stateActive

      The equivalent to 'ON' for the selected device (green).

   .. attribute:: stateInactive

      The equivalent to 'OFF' for the selected device (red).


.. module:: nicos.guisupport.typedvalue

.. class:: DeviceValueEdit

   This widget presents a suitable child widget (or child widgets) for the user
   to enter or edit the value of a NICOS device.  The value is determined based
   on the device's :attr:`valuetype` attribute.

   For example, for the default "float" valuetype, a normal line edit is
   presented with a ``QDoubleValidator`` applied.  For a valuetype of ``oneof(a,
   b, c)``, a combo box with the different values is presented.

   Properties:

   .. attribute:: dev

      The device whose value should be edited.

   .. attribute:: useButtons

      If true (not the default), present buttons for some few value types
      (e.g. ``oneof`` with less than three alternatives).  This is only useful
      if the widget is meant to directly execute a move action.

   .. attribute:: updateValue

      If true (not the default), update the value in the widget from the device
      value whenever the device value changes.  Otherwise, the value is only
      taken from the device when the widget is first initialized for this device
      (i.e. the :attr:`dev` property is set).

   This widget, as an interactive widget, can emit two signals:

   .. attribute:: dataChanged

      This is emitted without arguments when the value in the widget changes.
      Call :meth:`getValue` to query the new value.

   .. attribute:: valueChosen

      This is emitted with the chosen value when the user directly chooses a
      value through a button (see :attr:`useButtons`).

   It also provides public API methods to manipulate the current value:

   .. method:: getValue()

      Return the current value of the widget.  Its type will match the valuetype
      of the selected device.

   .. method:: setValue(value)

      Set the current value of the widget.  If the value does not match the
      valuetype of the device, the widget will be initialized with an "empty"
      value depending on the valuetype.


.. class:: DeviceParamEdit

   This is a subclass of :class:`DeviceValueEdit` that allows editing of
   parameters of a device.  It works just like the parent class, except that it
   has an additional property to specify the parameter name:

   .. attribute:: param

      The name of the parameter (of the device selected with :attr:`dev`) whose
      value should be edited.

