============
Contributing
============

The ``DataCatalog`` package is designed to be extended. It is quite tractable
for contributors not deeply familiar with the codebase or schema to extend
either.

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

- ``--bootstrap`` : run tests that check the developer environment
- ``--delete`` : enable tests that delete **local** Mongodb records
- ``--longrun`` : enable tests that might take >500 msec to run
- ``--networked`` : enable tests that require external network access

.. code-block:: console

    make tests PYTEST_OPTS="-k jsonschemas"

Test MongoDB instance
^^^^^^^^^^^^^^^^^^^^^

A MongoDB 3.6 Docker service is bundled with our tests, and is required to be
active before most tests can be run. You can stand it up using ``make`` targets
or via the ``docker-compose.yml`` file found in ``docker/``.

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

*Here is how to set up a TACC.cloud client*

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

Documentation
-------------

This project uses Google-style Python documentation strings rendered via
Autodoc and the Napoleon preprocessor.

- `Google Python Style <https://google.github.io/styleguide/pyguide.html>`_
- `Example Google style docstrings <https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google>`_
- `Napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_

.. code-block:: console
   :caption: Regenerate all project documentation

   make docs-clean && make docs
