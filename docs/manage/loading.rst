===========================
Loading Records from a File
===========================

The bootstrap scripts named **manage_*.py** look for JSON files in directories
under ``bootstrap`` corresponding to the collection they manage. The JSON files
can be individual records, or a JSON list of multiple records.

Here's a worked example to illustrate the process"

Bootstrapping a File Record
---------------------------

Write a JSON file resembling this one to ``bootstrap/files/file555.json``. The
file is written to conform to the `file <https://schema.catalog.sd2e.org/schemas/file.json>`_ schema.

.. code-block: json
   :caption: file-555.json

   {
      "name": "/uploads/tacc/example/555.txt",
      "type": "PLAIN",
      "level": "0",
      "file_id": "file.tacc.90005",
      "child_of": [
          "1049d8dd-e879-53e8-a916-f975f1785c29"
      ]
   }

.. code-block:: console

   $ python -m bootstrap.manage_files auto -localhost
   manage_files.py.INFO: Registered /uploads/tacc/example/555.txt

Now, if you search your local ``files`` collection for a record with the
``name``, you will get back a record resembling the following:

.. code-block: json

   {
       "name" : "/uploads/tacc/example/555.txt",
       "type" : "PLAIN",
       "level" : "0",
       "file_id" : "file.tacc.90005",
       "child_of" : [
           "1049d8dd-e879-53e8-a916-f975f1785c29"
       ],
       "uuid" : "10597f0f-2ce3-5520-a5a2-ecf40b0e4ad1",
       "_properties" : {
           "created_date" : ISODate("2019-02-13T12:29:23.000+0000"),
           "modified_date" : ISODate("2019-02-13T12:29:23.000+0000"),
           "revision" : 0,
           "source" : "testing"
       },
       "_admin" : {
           "owner" : "sd2eadm",
           "project" : "sd2e-community",
           "tenant" : "sd2e"
       }
}

More detail and examples is forthcoming but hopefully this is enough to get a
flavor for what the management tools allow one to accomplish.
