***************
Introduction
***************

.. contents::

Requirements
============

`Python <https://www.python.org/>`_ is needed to run the |CI|.

Invoke Command
==================

The following command can be used to start the |CI|

::

	Usage: cache-inspector [options]

Options
-------

.. program:: cache-inspector

.. option:: -h, --help

    The help command shows the usage and options less verbose.

.. option:: -c, --cache

   The cache server and port the |CI| is going to connect to. The default
   server is localhost and the default port is 14869.

.. option:: -p, --prefix

    The prefix limits the result of keys to show only those that use the given
    prefix. The default is no prefix at all. Which means all keys without
    exception are shown.

If no option is given the first key is used as the cache server and
the second as the prefix.

Examples:

::

    cache-inspector -c 196.168.14.243:14869 -p "nicos"

::

    cache-inspector localhost:14869


