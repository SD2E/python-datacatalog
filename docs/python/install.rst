============
Installation
============

.. _where_available:

Where is DataCatalog available?
-------------------------------

``DataCatalog`` is installed by default in ``sd2e/python3``, ``sd2e/python2``,
``sd2e/reactors:python2-edge``, and ``sd2e/reactors:python3-edge`` base images.
It will soon be available by default inside the Jupyter notebooks enviroment.
You can install it locally or embed it in your own projects as well.

.. _what_version:

What version to install
-----------------------
``DataCatalog`` is under constant development. Some new or updated features may
be missing from the public, versioned release. If you need those capabilities,
you will want to install from source.

.. _from_pipy:

Latest stable release from PiPy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install the latest versioned release `releases <https://pypi.org/project/python-datacatalog/#history>`_.

.. code-block:: console

    pip install python-datacatalog

For a specific version:

.. code-block:: console

    pip install python-datacatalog==0.2.0


.. _from_source:

Latest stable release from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also install the latest release from source code, which is available on
GitHub.

First, obtain the source code.

.. code-block:: console

    git clone https://github.com/SD2E/python-datacatalog

Change into the ``python-datacatalog`` directory and choose the branch you want
to install. The most recent versioned release is on the ``master`` branch. The
latest stable, but unreleased code, is on ``develop``, and there may be other
feature branches available. Here's an example of installing the ``develop``
branch.

.. code-block:: console

    cd python-datacatalog
    git checkout develop

If you have `GNU make <https://www.gnu.org/software/make/manual/make.html>`_
installed in your system, you can install ``AgavePy`` for Python 3 as follows:

.. code-block:: console

    make install
