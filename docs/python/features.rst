============
Key Features
============

- Extensible data model that represents:
   - Topics, designs, experiments, samples, and measurement artifacts
   - Reference data files
   - Analysis and ETL pipelines and jobs
   - Complex types like temperature, liquid media component, and time point
   - Linkages to external data via URI and typed identifiers
   - Complex parentage and derivation relationships
- Pythonic search API plus support for MongoDB-compatible JSON queries
- Data model defined and extended using JSONschema Draft 7
- Documents mantain creation, update, revision, and source reference
- JSON-diff journal enables fine-grained change tracking
- Support for authenticated document updates is available
- Multiple tenants, projects, and users are supported
- Leverages clustered MongoDB for scalability and durability

=========
Use Cases
=========

``DataCatalog`` is currently a basis for code that:

- Transforms and load lab-provided metadata traces into a project Data Catalog
- Captures and manage fixity for raw and processed data products
- Describes ETL and processing pipelines and jobs
- Helps with aggregate reporting and integrity checking
- Provides RESTful web services and other user interfaces
- Constructs and maintains project Science Tables
