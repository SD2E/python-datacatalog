.. _schema_add_filetype:

=========
Filetypes
=========

The filetypes module provides two key functions in the Data Catalog system.
First, it enumerates over 700 distinct ways of storing structured information
in a file, with each format assigned a distinct human-readable string
identifier (i.e. ``RICHTEXT`` or ``JSON``). Second, it provides a robust
mechanism for identifying the format of a file using a combination of its
name, binary signature, and in some cases, its contents.

Two methods of identification are currently implemented. The first is **rules**,
which applies a collection of regular expressions to a filename to determine
its type. This is very fast and doesn't require physical access to the file.
The second is **mime**, which uses the FreeDesktop.org MIME classification
system for file typing. The mime method can inspect file contents, and thus
may only be used where there's a guarantee of file access.

Only extension of the **rules** mechanism is covered here.

Add a file type
---------------

Add an entry to ``FILETYPES`` in ``datacatalog.filetypes.ruleset.py`` following
this template: ``('LOG', 'Log file', ['.err$', '.out$', '.log$'])``.

The fields are, in order:

* Label: This is the searchable 'type' in Data Catalog
* Description: Human-readable definition of the file type
* Patterns: List of one or more Python regular expressions for filename matching

Note that the rules are evaluated in order, with the first match being
returned. This is fast, but one must be aware of ordering conflicts when adding
new entries to ``FILETYPES``

Test out the new rule, then open a pull request containing your improvements.

.. code-block:: pycon

   >>> filetypes.infer_filetype('captains.log')
   AttrDict({'label': 'LOG', 'comment': 'Log file'})
   >>> assert 'LOG' in filetypes.listall_labels()
   >>> filetypes.validate_label('LOG')
   True


Update a file type
------------------

Change the matching patterns in the select member of ``FILETYPES``. Test the
new behavior as outlined in the section above on adding a new type, then open
a pull request containing your improvements.
