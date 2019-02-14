=============
Configuration
=============

The repository relies on a few sources of configuration truth when it is
used in interactive mode. These are outlined below.

Project Configuration
---------------------

config.yml
##########

An example of this file is included with the repository. It provides a set of
database environment configurations (production, staging, etc), as well as
some values controlling logging behavior, stopwords for the Google Drive
integration used to define Challenge Problems and Experiment Requests, and so
on. Because this file contains sensitive information, it is prevented from
being checked into git via an entry in ``.gitignore``.

.gitignore
##########

The current contents of this file keep Python cache files, secret credentials,
and general pollution out of the git repository. Edit it with extreme caution.

setup.cfg
#########

This file controls behavior of several Python support tools like the Flake8
linter, Pytest, Pylint, etc.

conftest.py
###########

This is a more detailed configuration and setup file for Pytest.

setup.py
########

This file controls how the ``python-datacatalog`` package is installed.

Google API Credentials
----------------------

Integration with Google Drive is used to discovery Challenge Problem names and
Experiment Request documents. To activate API integration requires a
``service_account.json`` file and that the corresponding contents of
``config.yml`` match the contents of the service account file. Because the
service account file contains sensitive information, it is prevented from
being checked into git via an entry in ``.gitignore``.

.. note:: It is not mandatory to activate the Google API integration unless you
   need to regenerate the ``challenges`` and ``experiment_designs`` collections
   and JSON schema definitions.

.. only::  subproject and html

   Indices
   =======

   * :ref:`genindex`

