.. _gui-panels:

Writing Panels
==============

To write a new panel, derive from this base class:

.. module:: nicos.clients.gui.panels

.. class:: Panel(parent, client)

   The Panel class constructor a Qt *parent* widget and a *client* object (see
   :ref:`gui-client`).  ``Panel.__init__`` sets the following attributes on the
   panel objects:

   * ``client`` - the client object
   * ``parentwindow`` - the Qt parent window
   * ``mainwindow`` - a reference to the GUI main window
   * ``log`` - a :class:`logging.Logger` object to use for internal logging

   .. attribute:: panelName

      This class attribute should be set to something unique to the panel.  It
      is used for saving settings.

   Methods that you can override:

   .. method:: setOptions(options)

      Called with the *options* dictionary given as keywords by the panel
      configuration in the GUI config file.  Usually you should check if a given
      option is in the dictionary, and assume a default value if not.

   .. method:: setExpertMode(expert)

      Called when the GUI's "expert mode" is switched on or off.  *expert* is a
      boolean.

   .. method:: loadSettings(settings)

      Called when the panel should load its state and user settings from the
      given QSettings object.

   .. method:: saveSettings(settings)

      Called when the panel should save its state and user settings to the given
      QSettings object.

   .. method:: setCustomStyle(font, back)

      Called with a QFont object and a QColor object.  The panel should set the
      font of its main (text-based) widget(s) to the *font* and its background
      color to *back*.

   .. method:: getToolbars()

      Called to request any toolbars that the panel wants to provide (and that
      are then added to the window that contains the panel).  Return a list of
      QToolBar objects (or an empty list).

   .. method:: getMenus()

      Called to request any menus that the panel wants to provide (and that
      are then added to the window that contains the panel).  Return a list of
      QMenu objects (or an empty list).

   .. method:: hideTitle()

      If the panel has an obvious "title" label, it should be hidden when this
      method is called.  (This is called when the panel is placed in a dock
      widget, which has its own title label.)

   .. method:: requestClose()

      Called when the user wants to close the window containing the panel.  This
      method should return ``False`` if the window cannot be closed at the
      present time.  For example, the editor panel asks the user whether a dirty
      file should be saved, and clicking "Cancel" in that dialog box will
      prevent closing the window.

   .. method:: updateStatus(status, exception=False)

      Called when the current script status changes.
