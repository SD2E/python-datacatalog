.. _python_features:

============
Key Features
============

Data Catalog design is based on over 30 years of collective experience with
integrating and managing large, measured data. Its data model includes:
   - Topics, designs, experiments, samples, and measurement artifacts
   - Reference data files
   - Analysis and ETL pipelines and jobs
   - Linkages with external resources
   - Complex types like temperature, liquid media component, and time point
   - Sophistcated parentage and derivation relationships
   - Multiple data processing levels

Furthermore, it is designed to be easy to extend and maintain, with strong
models of document history, delegated or deferred edit authority, and fine-
grained tracking of ownership and attribution:
- Data model defined and extended using JSONschema Draft 7
- Documents mantain creation, update, and revision history
- Document- and role-level authorization for edits and updates
- Support for multiple tenants, projects, and users

=========
Use Cases
=========

Data Catalog code and services are currently used to:

- Transform and load lab-provided metadata traces into a project Data Catalog
- Capture and verify fixity for raw and processed data products
- Describe and manage ETL and processing pipelines and jobs
- Support aggregate reporting and integrity checking
- Enable data discovery amd exploration
