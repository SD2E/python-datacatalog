db.getCollection("jobs").aggregate(

	// Pipeline
	[
		// Stage 1
		{
			$match: {
			    "child_of": { "$not": {"$size": 0} },
			    "state": { "$in": ["FINISHED", "VALIDATED"] }
			}
		},

		// Stage 2
		{
			$lookup: {
			    "from": "pipelines",
			    "localField": "pipeline_uuid",
			    "foreignField": "uuid",
			    "as": "nc_rnaseq_jobs"
			}
		},

		// Stage 3
		{
			$match: {
			    "nc_rnaseq_jobs.name": {
			        // DEV
			         //"$regex" : /^Pro[et][et]omics Aggregator Pipeline/i
			         "$regex" : /^RNA-seq*/i
			    }
			}
		},

		// Stage 4
		{
			$lookup: {
			    "from": "experiments",
			    "localField": "child_of",
			    "foreignField": "uuid",
			    // DEV
			    //"as": "experiment_proteomics_jobs"
			    "as": "experiment_rnaseq_jobs"
			}
		},

		// Stage 5
		{
			$unwind: "$experiment_rnaseq_jobs"
			// DEV
			// "$experiment_proteomics_jobs
		},

		// Stage 6
		{
			$lookup: {
			    "from": "experiment_designs",
			    "localField": "experiment_rnaseq_jobs.child_of",
			    "foreignField": "uuid",
			    // DEV
			    // "as": "experiment_design_proteomics_jobs"
			    "as": "experiment_design_rnaseq_jobs"
			}
		},

		// Stage 7
		{
			$unwind: "$experiment_design_rnaseq_jobs"
		},

		// Stage 8
		{
			$addFields: {
			    "derived_from": {
			        "$ifNull": [ "$experiment_rnaseq_jobs.derived_from", ["unspecified"] ]
			    }
			}
		},

		// Stage 9
		{
			$lookup: {
			    "from": "files",
			    "localField": "derived_from",
			    "foreignField": "uuid",
			    "as": "experiment_design_files_rnaseq_jobs"
			}
		},

		// Stage 10
		{
			$lookup: {
			    "from": "files",
			    "localField": "uuid",
			    "foreignField": "child_of",
			    "as": "experiment_design_rnaseq_jobs_outputs"
			}
		},

		// Stage 11
		{
			$lookup: {
			    "from": "files",
			    "localField": "product_patterns.derived_from",
			    "foreignField": "name",
			    "as": "input_dfs"
			}
		},

		// Stage 12
		{
			$lookup: {
			    "from": "jobs",
			    "localField": "input_dfs.child_of",
			    "foreignField": "uuid",
			    "as": "df_job"
			}
		},

		// Stage 13
		{
			$unwind: "$df_job"
		},

		// Stage 14
		{
			$addFields: {
			"input_gff":"$df_job.data.inputs.path_gff"
			}
		},

		// Stage 15
		{
			$project: {
			    "_id": false,
			    "experiment_id": "$experiment_rnaseq_jobs.experiment_id",
			    "experiment_design_id": "$experiment_design_rnaseq_jobs.experiment_design_id",
			    "storage_system": {
			        "$cond": {
			            "if": { "$eq": [ { "$arrayElemAt": [ "$derived_from", 0 ] }, "unspecified" ] },
			            "then": "unspecified",
			            "else": { "$arrayElemAt": ["$experiment_design_files_rnaseq_jobs.storage_system", 0] }
			        }
			    },
			    "samples_json": {
			        // the manifest
			        "$cond": {
			            "if": { "$eq": [ { "$arrayElemAt": [ "$derived_from", 0 ] }, "unspecified" ] },
			            "then": "unspecified",
			            "else": { "$arrayElemAt": ["$experiment_design_files_rnaseq_jobs.name", 0] }
			        }
			    },
			    "job_uuid": "$uuid",
			    "last_updated": "$updated",
			    "state": "$state",
			    "archive_path": "$archive_path",
			    "outputs": "$experiment_design_rnaseq_jobs_outputs.name",
			    "input_gff": "$input_gff"
			}
		},

		// Stage 16
		{
			$group: {
			    "_id": {
			        "experiment_id": "$experiment_id",
			        "experiment_design_id": "$experiment_design_id",
			        "storage_system": "$storage_system",
			        "samples_json": "$samples_json"
			    },
			    "jobs": {
			        "$push": {
			            "job_uuid": "$job_uuid",
			            "last_updated": "$last_updated",
			            "state": "$state",
			            "archive_path": "$archive_path",
			            "outputs": "$outputs",
			            "input_gff": "$input_gff"
			        }
			    }
			}
		},

		// Stage 17
		{
			$sort: {
			    "_id.experiment_id": 1
			}
		},

	]

	// Created with Studio 3T, the IDE for MongoDB - https://studio3t.com/

);
