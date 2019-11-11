# Note: Read and understand https://gitlab.sd2e.org/sd2program/python-datacatalog/merge_requests/190 
# Before running!

import pymongo
from datacatalog.identifiers.typeduuid import catalog_uuid

# Update this to target production
# This should only need to be done once
dbURI = "mongodb://catalog:catalog@localhost:27017/?authSource=admin"
 
client = pymongo.MongoClient(dbURI)
experiment_designs = client.catalog_local.experiment_designs
experiments = client.catalog_local.experiments

design_uri_map = {}

# Find designs with the same URI - these are candidates for remapping and deletion
design_matches = experiment_designs.find({})
for design_match in design_matches:
    uri = design_match["uri"]
    if uri is not None:
        if uri not in design_uri_map:
            design_uri_map[uri] = []
        design_uri_map[uri].append(design_match)

for key in design_uri_map:
    design_len = len(design_uri_map[key])
    if design_len > 2:
        # This would be very unusual - check these cases manually if found
        raise ValueError("More than 2 designs for a URI? {}".format(key))
    elif design_len == 2:
        # We have a new design and an old design. Find experiments linked to the old design,
        # remap them to the new design, and remove the old design.
        old_design = None
        new_design = None   
        for design in design_uri_map[key]:
            # old designs have uuids derived from the experiment design id
            # new designs have uuids derived from the uri
            design_id_uuid = catalog_uuid(design["experiment_design_id"], uuid_type='experiment_design')
            uri_uuid = catalog_uuid(design["uri"], uuid_type='experiment_design')

            if design["uuid"] == design_id_uuid:
                old_design = design
            elif design["uuid"] == uri_uuid:
                new_design = design
            else:
                raise ValueError("Could not identify old/new design for {}".format(key))

        if old_design is not None and new_design is not None and old_design != new_design:
            experiment_matches = experiments.find( { "child_of" : [old_design["uuid"]] })
            e_match_list = []

            for experiment_match in experiment_matches:
                e_match_list.append(experiment_match)

            if len(e_match_list) >= 1:
                print("Found matching experiments, remapping for: {} old design uuid {} new design uuid {}".format(key, old_design["uuid"], new_design["uuid"]))
                for e_match in e_match_list:
                    record_id = e_match["_id"]
                    new_child_of = [new_design["uuid"]]
                    print("Remapping {} from {} to {}".format(record_id, e_match["child_of"], new_child_of))

                    experiments.update({ "_id" : record_id },
                    { "$set":
                        {
                            "child_of" : new_child_of
                        }
                    })
            # after remapping, regardless if any experiments are found, delete the old design
            print("Removing design: {}".format(old_design["uuid"]))
            experiment_designs.delete_one({'uuid' : old_design["uuid"]})
