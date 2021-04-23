=======================
TA4 Pipeline Job Status
=======================

This dashboard provides real-time status update of individual experiment request submission, data uploads,
metadata validation, ETL processing and links to data products in a tabular format for deep dive.

Data Fields Included
--------------------
The dashboard populates the following columns for each experiment run when data is available:
   - experiment_id
   - experiment_reference, with link to the experiment request GoogleDoc
   - protocol
   - OvNgt (overnight growth period)
   - Recov Lps (recovery loops)
   - SR path, which is a link to the structured request JSON document
   - Submitted date/time
   - Uploaded date/time
   - path (for uploaded data), which is a link to the uploaded lab trace
   - Converted date/time, where conversion is for transforming the lab trace into the standardized format
   - path (for converted lab trace), which is a link to the standardized lab trace
   - mtypes, a summary of measurement types included in the uploaded data (P - PLATEREADER, F - FLOW, R - RNASeq, D - DNASeq, C - CFU) 
   - Comp passed, a boolean showing if the lab trace has passed the metadata validation
   - Annotated, a boolean showing if controls have been annotated in the standardized lab trace
   - date/time (for annotation)
   - path (for annotation), which is a link to the annotated lab trace
   - Ingest date/time, for when data is loaded into the catalog
   - database, mongodb database name for the catalog
   - FLOW color_model, flow ETL run using TASBE on a mini dataset for checkout the color model
   - date/time (for flow color_model run)
   - archive_path (for flow color_model run)
   - FLOW whole_dataset, flow ETL run using TASBE on the whole dataset
   - date/time (for flow whole_dataset run)
   - archive_path (for flow whole_dataset run)
   - RNA-seq qc_metadata
   - date/time (for RNA-seq qc_metadata run)
   - input_gff (for RNA-seq)
   - archive_path (for RNA-seq)
   - obs_load date/time, for when observation catalog was last run
   - path (for obs_load)

How to use the dashboard
------------------------
   - Use the search widget to search for experiment(s) for a given experiment reference, experiment_id, comp passed using substring or full text
   - Click a column header to sort the records by that column
   - Hover the mouse over a link to view the corresponding URL
   - Click on the experiment reference link for an experiment to view the experiment request document
   - Click the SR path link to view the structure request document when available
   - Click an archive_path link to view content contained in the archive_path folder

Resources
---------

- `Source (Github Mirror) <https://gitlab.sd2e.org/sd2program/etl-pipeline-support/blob/2_0/catalog_views/redash_sr_status>`_