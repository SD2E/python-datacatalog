.. _python_develop:

=============================
Developing the Python Package
=============================

The ``datacatalog`` package is designed to be extended. It is quite tractable
for contributors not deeply familiar with the codebase or schema to extend
either.

Dependencies
------------

There are a few dependencies that can't be resolved via Python package managers:
    1. Python 3.5+
    2. Docker CE 17+
    3. Docker Compose
    4. GNU Make
    5. Git
    6. On MacOS X (available via Homebrew):
        * libmagic
        * shared-mime-info

Get the source code
-------------------

Obtain the source code and checkout the ``develop`` branch.

.. code-block:: console

    git clone https://github.com/SD2E/python-datacatalog
    cd python-datacatalog
    git checkout develop
    git pull origin develop

Unit testing
------------

All unit tests are avaiable via the Gnu Make target ``tests``

.. code-block:: console

    make tests

Several of the bundled tests exercise reading and writing from a toy instance
of MongoDB, interact with the Agave APIs, or leverage Google Drive APIs. They
are, save for the MongoDB tests, gated behind Pytest options which can be sent
to the ``make tests`` target via ``PYTEST_OPTS``. For example, here is how to
force tests that have a long run time to execute:

.. code-block:: console

    make tests PYTEST_OPTS="--longrun"

Here is an example of just running the ``jsonschemas`` tests.

The current list of ``pytest`` extended flags is:

- ``--bootstrap`` : run tests that setup and check the developer environment
- ``--delete`` : enable tests that delete **local** Mongodb records
- ``--longrun`` : enable tests that might take >500 msec to run
- ``--networked`` : enable tests that require external network access

.. code-block:: console

    make tests PYTEST_OPTS="-k jsonschemas"

Test MongoDB instance
^^^^^^^^^^^^^^^^^^^^^

A MongoDB 4.1.7 Docker service is bundled with our tests, and is required to be
active for most tests. Stand it up using ``make`` targets or via the included
``docker-compose.yml`` file.

.. code-block:: console

   :caption: Start or stop local MongoDB

   cd python-datacatalog
   # start the service
   make mongo-up
   # shut it down
   make mongo-down

Verify that the local database server is usable in the test suite as follows:

.. code-block:: console

    make smoketest-mongo-local

*What to do if this test fails even after starting the server*

TACC.cloud API client
^^^^^^^^^^^^^^^^^^^^^

Several functions that rely on an active TACC.cloud API client. You may need to
set one up on your development system. You can check with the following test:

.. code-block:: console

    make smoketest-agave

Details on how to set up a TACC.cloud client can be found in the `API User Guide <https://sd2e.github.io/api-user-guide/docs/01.install_cli.html>`_.

Local config.yml
^^^^^^^^^^^^^^^^

For compatibility with the Reactors SDK, this package uses ``config.yml``
for run-time configuration. Check the status of your configuration file using
this test:

.. code-block:: console

    make smoketest-config

*Here is how to set up config.yml*

Google Drive service account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An active integration with Google Drive using a service account is required to
rebuild to populate the challenge problem and experiment design MongoDB, and,
by extension, to rebuilt the project schema. You will need to obtain a valid
``service_account.json`` file from project staff or provision one yourself.
Check the status of your Google Drive integration with this test:

.. code-block:: console

    make smoketest-google

*Here is how to set an authorized Google Drive service account*

Bootstrapping Local Data
------------------------

Many of the tests require some pre-loaded data in the local MongoDB. These can
be loaded using make targets that exercise the bundled management scripts in
the ``bootstrap`` directory. Once all the developer smoketests are passing:

.. code-block:: console

    make bootstrap-tests

You should be able to run the basic unit tests now with ``make tests``

Documentation
-------------

This project uses Google-style Python documentation strings rendered via
Autodoc and the Napoleon preprocessor.

- `Google Python Style <https://google.github.io/styleguide/pyguide.html>`_
- `Example Google style docstrings <https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google>`_
- `Napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_

The docs are built using Sphinx and some Makefile targets. An example console
session is illustrated below:

.. code-block:: console

   $ make docs-clean && make docs-autodoc && make docs
   cd docs && make clean
   Removing everything under '_build'...
   cd uml && pyreverse -o png ../datacatalog
   parsing ../datacatalog/__init__.py...
   ...
   The HTML pages are in _build/html

A couple of notes:
1. There will be warnings in **RED**. Some will be significant and some are just unsupressable noise. Look for outright errors and failures.
2. If you are iterating  rapidly on just documentation and have not changed any Python code, you can omit the ``make docs-autodoc`` command
