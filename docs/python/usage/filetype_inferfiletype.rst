========================
Infer the type of a file
========================

The ``filetypes`` module supports both rule- and content-based detection of
file type. Using the content-based method requires that the code is run on a
host with physical access to the target file.

.. code-block:: pycon

   >>> from datacatalog.filetypes import infer_filetype
   >>> infer_filetype('foo.pdf')
   AttrDict({'label': 'PDF', 'comment': 'PDF document'})
   >>> infer_filetype('foo.pdf').label
   'PDF'
   >>> infer_filetype('foo.pdf').comment
   'PDF document'
   >>> infer_filetype('foo.pdf', check_exists=True)
   ...
   OSError: foo.pdf does not exist or is not accessible

The **label** for a given file type is what the Data Catalog uses for
``file.type``,  while **comment** is simply a human-readable description of
the type.

