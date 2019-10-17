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
			    "as": "pipeline"
			}
		},

		// Stage 3
		{
			$match: {
			    "pipeline.name": {
			        "$regex" : /^Pro[et][et]omics Aggregator Pipeline/i
			    }
			}
		},

		// Stage 4
		{
			$lookup: {
			    "from": "experiments",
			    "localField": "child_of",
			    "foreignField": "uuid",
			    "as": "experiment"
			}
		},

		// Stage 5
		{
			$unwind: "$experiment"
		},

		// Stage 6
		{
			$lookup: {
			    "from": "experiment_designs",
			    "localField": "experiment.child_of",
			    "foreignField": "uuid",
			    "as": "experiment_design"
			}
		},

		// Stage 7
		{
			$unwind: "$experiment_design"
		},

		// Stage 8
		{
			$unwind: "$product_patterns"
		},

		// Stage 9
		{
			$lookup: {
			    "from": "files",
			    "localField": "uuid",
			    "foreignField": "child_of",
			    "as": "outputs"
			}
		},

		// Stage 10
		{
			$lookup: {
			    "from": "files",
			    "localField": "product_patterns.derived_from",
			    "foreignField": "name",
			    "as": "inputs"
			}
		},

		// Stage 11
		{
			$project: {
			    "_id": false,
			    "experiment_id": "$experiment.experiment_id",
			    "experiment_design_id": "$experiment_design.experiment_design_id",
			    "storage_system": "$archive_system",
			    "experiment_design_document": "$experiment_design.uri",
			    "job_uuid": "$uuid",
			    "last_updated": "$updated",
			    "state": "$state",
			    "archive_path": "$archive_path",
			    "outputs": "$outputs.name",
			    "protein_score_threshold": "$data.protein_score_threshold"
			}
		},

		// Stage 12
		{
			$group: {
			    "_id": {
			        "experiment_id": "$experiment_id",
			        "experiment_design_id": "$experiment_design_id",
			        "storage_system": "$storage_system",
			        "experiment_design_document": "$experiment_design_document"
			    },
			    "jobs": {
			        "$push": {
			            "job_uuid": "$job_uuid",
			            "pipeline_uuid": "$pipeline_uuid",
			            "last_updated": "$last_updated",
			            "state": "$state",
			            "archive_path": "$archive_path",
			            "outputs": "$outputs",
			            "parameters": {
			                "protein_score_threshold": "$protein_score_threshold"
			            }
			        }
			    }
			}
		},

		// Stage 13
		{
			$sort: {
			    "_id.experiment_id": 1
			}
		},

	]

	// Created with Studio 3T, the IDE for MongoDB - https://studio3t.com/

);
