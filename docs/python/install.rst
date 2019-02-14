.. _python_install:

============
Installation
============

.. _what_version:

What version to install
-----------------------
The package is under constant development. Some new or updated features may
be missing from the public versioned release. To access these capabilities,
it will be necessary to install from source.


.. _from_pipy:

Latest stable release from PiPy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install the latest versioned release `releases <https://pypi.org/project/python-datacatalog/#history>`_.

.. code-block:: console

    pip install python-datacatalog

For a specific version:

.. code-block:: console

    pip install python-datacatalog==0.1.4


.. _from_source:

Latest stable release from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also install the latest release from source code, which is available on
GitHub.

First, obtain the source code.

.. code-block:: console

    git clone https://github.com/SD2E/python-datacatalog

Change into the ``python-datacatalog`` directory and choose the branch you want
to install. The most recent versioned release is on the ``master`` branch.
Stable, but unreleased code, is on ``develop``, and there may be other
feature branches available.

Here's an example of installing the ``develop`` branch.

.. code-block:: console

    $ cd python-datacatalog
    $ git checkout develop
    $ make install
    # Alternatively...
    $ python3 setup.py install

Git Repository Branches and Tags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------+--------------+-----------------+-----------+------------------------+
| Type   | Name         | Schema          | Code      | Recommended            |
+========+==============+=================+===========+========================+
| branch | ``1_0_0``    | 1.0.0           | 0.1.x     | Maintainers            |
+--------+--------------+-----------------+-----------+------------------------+
| tag    | ``v1.0.0``   | 1.0.0           | 0.1.4     | Maintainers            |
+--------+--------------+-----------------+-----------+------------------------+
| branch | ``2_0_0``    | 2.0.0-dev       | 0.2.x     | Developers/Maintainers |
+--------+--------------+-----------------+-----------+------------------------+
| tag    | ``v2.0.0``   | **2.0.0-final** | **0.2.0** | **Users**              |
+--------+--------------+-----------------+-----------+------------------------+
| branch | ``master``   | 2.0.0-final     | 0.2.0     | Developers             |
+--------+--------------+-----------------+-----------+------------------------+
| branch | ``develop``  | 2.0.x           | 0.2.x     | Developers/Maintainers |
+--------+--------------+-----------------+-----------+------------------------+
| branch | ``gh-pages`` | Latest          | Latest    | Nobody                 |
+--------+--------------+-----------------+-----------+------------------------+
