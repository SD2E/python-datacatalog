============================
Fetch document(s) by UUID(s)
============================

Using an instance of the ``CatalogManager`` class, it is possible to fetch one
or more Data Catalog documents by their UUID.

.. code-block:: pycon

   >>> from settings import settings
   >>> from datacatalog.managers import CatalogManager
   >>> cm = CatalogManager(settings.mongodb)
   >>> cm.get_by_uuid('102e95e6-67a8-5a06-9484-3131c6907890')
   {'title': 'Pipeline Automation Tests', 'experiment_id': 'experiment.tacc.10001', 'child_of': ['1144f727-8827-5126-8e03-f35e8cb6f070'], 'uuid': '102e95e6-67a8-5a06-9484-3131c6907890'}
   >>> cm.get_by_uuids(['1027aa77-d524-5359-a802-a8008adaecb5', '102edd93-29d6-5483-b60b-8dfd4d094b9c'])
   [{'title': 'Contestant Number One', 'child_of': ['11417253-69fe-5902-bcb4-033a2f1ba784', '114bb9f2-1483-5195-9dd6-78ea91b70291'], 'uuid': '1027aa77-d524-5359-a802-a8008adaecb5', 'experiment_id': 'experiment.tacc.10003'}, {'title': 'NAND Gate Expt 1', 'uuid': '102edd93-29d6-5483-b60b-8dfd4d094b9c', 'experiment_id': 'experiment.ginkgo.10001', 'child_of': ['114e742e-e67a-5e99-bc04-c60d1eec9a41']}]
