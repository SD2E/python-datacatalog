Validate a UUID
===============

It is possible to validate that a given UUID is a Data Catalog TypedUUID.

.. code-block:: pycon

   >>> from datacatalog.identifiers import typeduuid
   >>> typeduuid.validate('1027aa77-d524-5359-a802-a8008adaecb5')
   True
   >>> typeduuid.validate('1557aa77-d524-5359-a802-a8008adaecb5', permissive=True)
   False
   >>> typeduuid.validate('1557aa77-d524-5359-a802-a8008adaecb5')
   Traceback (most recent call last):
   ...
   ValueError: Not a valid TypedUUID

.. note:: Existence of the UUID is not checked, only its structural correctness.
