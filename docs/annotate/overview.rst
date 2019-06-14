========
Overview
========

A key design objective for user annotation is to allow analysts, data providers,
and even external collaborators to decorate metadata objects in the Data
Catalog and have those decorations propagate to records that are linked
downstream of the annotated item. For instance, adding a comment to sample
should mean that users working with that samples measurements and files, or even
derived data products, will have access to that sample-level annotation.

There are currently two forms of user-initiated annotations currently
implemented. Tags are short alphanumeric strings drawn from a controlled
vocabulary, while Text Annotations are free text documents with a an optional
subject line. Support for an Attribute-Value-Unit class of annotation is
forthcoming.
