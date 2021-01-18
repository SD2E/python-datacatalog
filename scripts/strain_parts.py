import pandas as pd
import pymongo
import sys

from synbiohub_adapter.query_synbiohub import *
from synbiohub_adapter.SynBioHubUtil import *
from sbol import *

def get_strain_uri_to_name_map_from_catalog(db_uri):
    print("db_uri: {}".format(db_uri))
    client = pymongo.MongoClient(db_uri)
    science_table = client.catalog_staging.science_table
    strains = science_table.aggregate([ 
        {"$group": { 
            "_id": {
                "strain_name": "$strain", 
                "strain_sbh_uri": "$strain_sbh_uri"
            }
        }} 
    ])
    strain_uri_to_name_map = {}
    strain_uri_to_name_map2 = {}
    for strain in strains:
        if "strain_name" in strain["_id"]:
            strain_name = strain["_id"]["strain_name"]

        if "strain_sbh_uri" in strain["_id"]:
            strain_sbh_uri = strain["_id"]["strain_sbh_uri"]
            if strain_sbh_uri != "NO PROGRAM DICTIONARY ENTRY":
                if strain_sbh_uri not in strain_uri_to_name_map:
                    strain_uri_to_name_map[strain_sbh_uri] = strain_name
                else:
                    if strain_sbh_uri not in strain_uri_to_name_map2:
                        strain_uri_to_name_map2[strain_sbh_uri] = []
                    strain_uri_to_name_map2[strain_sbh_uri].append(strain_uri_to_name_map[strain_sbh_uri])
                    strain_uri_to_name_map2[strain_sbh_uri].append(strain_name)

    # map2 should be empty
    print(f"strain_uri_to_name_map2: {strain_uri_to_name_map2}")
    return strain_uri_to_name_map
  
def get_strain_uri_to_parts_map_from_sbh(user, password):
    sbh_query = SynBioHubQuery(SD2Constants.SD2_SERVER)
    sbh_query.login(user, password)
    query = """PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX sbol: <http://sbols.org/v2#>
        PREFIX sd2: <http://sd2e.org#>
        SELECT ?strain (group_concat(distinct ?part;separator=",") as ?parts) (group_concat(distinct ?partName;separator=",") as ?partNames) WHERE {
            <https://hub.sd2e.org/user/sd2e/design/design_collection/1> sbol:member ?strain .
            ?strain sbol:role <http://purl.obolibrary.org/obo/NCIT_C14419> ;
                sbol:module ?sm .
            ?sm sbol:definition ?network .
            ?network sbol:role <http://purl.obolibrary.org/obo/NCIT_C20633> ;
                (sbol:module/sbol:definition)?/sbol:interaction/sbol:participation/sbol:participant/sbol:definition ?part .
            ?part sbol:type <http://www.biopax.org/release/biopax-level3.owl#DnaRegion> ;
                dcterms:title ?partName
        }
        GROUP BY ?strain"""
    output = sbh_query.fetch_SPARQL(SD2Constants.SD2_SERVER, query)
    strain_uri_to_parts_map = {}
    strain_parts_bindings = output["results"]["bindings"]
    for spb in strain_parts_bindings:
        strain_sbh_uri = spb["strain"]["value"]
        part_names = spb["partNames"]["value"].split(",")
        strain_uri_to_parts_map[strain_sbh_uri] = part_names
    
    return strain_uri_to_parts_map
    
def get_master_strain_to_parts_map(db_uri, sbh_user, sbh_pass):
    strain_uri_to_name_map = get_strain_uri_to_name_map_from_catalog(db_uri)
    strain_uri_to_parts_map = get_strain_uri_to_parts_map_from_sbh(sbh_user, sbh_pass)

    strain_name_to_parts_map = {}
    for strain_uri in strain_uri_to_parts_map.keys():
        if strain_uri in strain_uri_to_name_map.keys():
            strain_name_to_parts_map[strain_uri_to_name_map[strain_uri]] = strain_uri_to_parts_map[strain_uri]
            
    return strain_name_to_parts_map

# returns a dataframe of strains one-hot encoded with parts
def get_df_for_strains(strains, strain_name_to_parts_map):
    sub_map = {strain_name:strain_name_to_parts_map[strain_name] for strain_name in strains}
    row_list = []
    for strain in sub_map.keys():
        row = {"strain_name":strain, "parts":sub_map[strain]}
        row_list.append(row)
    
    df = pd.DataFrame(row_list)
    df2 = df.drop('parts', 1).join(pd.get_dummies(pd.DataFrame(df.parts.tolist()).stack()).astype(int).sum(level=0))

    return df2
    
def main():
    if len(sys.argv) < 4:
        print('python strain_parts.py db_uri sbh_user sbh_pass')
        sys.exit(2)

    strain_name_to_parts_map = get_master_strain_to_parts_map(sys.argv[1], sys.argv[2], sys.argv[3])
    strains_of_interest = [
        'UWBF_XOR_10', 
        'UWBF_NOR_01', 
        'MG1655_LPV3_LacI_AraC_Sensors_pBADmin_PsrA_pTac_AmeR', 
        'UWBF_XOR_01', 
        'MG1655_LPV3_LacI_AraC_Sensors_pBADmin_PsrA_pTac_AmeR_pPsrA_pAmeR_YFP'
    ]

    df = get_df_for_strains(strains_of_interest, strain_name_to_parts_map)
    print(df.head(5))
    
if __name__ == '__main__':
  main()