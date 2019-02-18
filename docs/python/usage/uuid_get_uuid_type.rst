=======================
Get the type for a UUID
=======================

You can learn the Data Catalog **type** for a given UUID with ``get_uuidtype``.

.. code-block:: pycon

   >>> from datacatalog.identifiers import typeduuid
   >>> typeduuid.get_uuidtype('1027aa77-d524-5359-a802-a8008adaecb5')
   'experiment
   >>> typeduuid.get_uuidtype('1557aa77-d524-5359-a802-a8008adaecb5')
   ...
   ValueError: 1557aa77-d524-5359-a802-a8008adaecb5 is not a known class of TypedUUID
