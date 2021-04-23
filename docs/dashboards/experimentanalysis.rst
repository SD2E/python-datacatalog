===================
Experiment Analysis
===================

This dashboard provides real-time status update of data converge (DC) and precomputed data table (PDT)
and links to products for easy lookup.

Data Fields Included
--------------------
The dashboard populates the following columns for each experiment reference run when data is available:
   - experiment_reference, with link to the experiment request GoogleDoc
   - protocol
   - OvNgt (overnight growth period)
   - Recov Lps (recovery loops)
   - mtypes, a summary of measurement types included in the uploaded data (P - PLATEREADER, F - FLOW, R - RNASeq, D - DNASeq, C - CFU) 
   - state, with two possible values: complete - when all associated experiment runs have passed metadata validation, 
     processed by flow ETL and validated if flow data is available; preview - when some experiment runs failed metadata
     validation or when flow data is available, missed flow ETL or haven't been validated.
   - DC date/time, for when data converge was last run
   - upload to DC in hours
   - DC output, link to where data converge output can be found
   - PDT date/time, for when the last precomputed data table analysis was run
   - upload to PDT in hours
   - finished analyses, a summary of analyses that have run (GA - growth analysis, PM - perform metrics, 
     FSP - fcs signal prediction, LDP - live dead prediction, WA - wasserstein, DG - Diagnose, OM - omics)
   - PDT output, link to where PDT analyses output can be found
   - visualization, link to the Escalation site for visualization of analysis results
   
How to use the dashboard
------------------------
   - Use the search widget to search for experiment(s) for a given experiment reference using substring or full text
   - Click a column header to sort the records by that column
   - Hover the mouse over a link to view the corresponding URL
   - Click on the experiment reference link to view the experiment request document
   - Click the jupyter link to view content contained in the corresponding folder for DC or PDT

Resources
---------

- `Source (Github Mirror) <https://gitlab.sd2e.org/sd2program/etl-pipeline-support/blob/2_0/catalog_views/redash_analysis>`_