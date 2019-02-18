=========
Databases
=========

There are currently three databases that you might connect to:

* ``catalog`` - The current **production** database containing validated metadata and linkages in the schema defined by the current numbered release of ``python-datacatalog`` package
* ``catalog_staging`` - A version of the database where the metadata records and schema conform to the ``develop`` branch of ``python-datacatalog``. It is the program's intent that the contents of **staging** are in sync with **production** but be forwarned that this is not always possible.
* ``catatlog_dev`` - This is an actively-developed instance of the database and schema. It is not intended to be reliable, stable, of information-complete.

For serious, reproducible work, please use **catalog**.

Retired Databases
-----------------

As the project schema evolves, older representations will be copied into
read-only databases named ``catalog_<version>`` where ``<version>`` is the
major and minor version number of the schema. For example, after the cutover
from v1 to v2 schemas in March 2019, the existing contents of ``catalog`` will
remain available for query as ``catalog_1_0``. NOte that retired databases will
**not** be updated.
