Omninotify
==========
Omninotify is a libary for displaying desktop notifications across different
platforms. It currently implements support for macOS and Freedesktop
notifications. The implementation provides a restricted subset of functionality
that exists on both platforms.

I made this library since I wanted a library to use with Weechat, which I use on
both macOS and Linux daily.


Example
-------
See `example.py <https://github.com/runfalk/omninotify/blob/master/example.py>`_
for examples on how to use it.


Requirements
------------
For macOS users the only requirement is ``terminal-notifier`` which must be
somewhere in the users' path. The recommended way to install
``terminal-notifier`` is by using `Homebrew <http://brew.sh/>`_:

.. code-block:: bash

   $ brew install terminal-notifier

For use on Linux (Freedesktop) a system installation of ``gi`` is required. On
Debian/Ubuntu this is installed by either ``python-gi`` or ``python3-gi``.
Additionally the the ``pydbus`` package is required:

.. code-block:: bash

   $ pip install pydbus

If it is used inside a virtual environment one can satisfy the ``gi`` dependency
by installing ``vext.gi``.
