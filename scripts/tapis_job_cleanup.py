import pymongo
import sys
from agavepy.agave import Agave

def get_tapis_jobs_for_experiment(db_uri, ex_id, agave=None):
    print(f"db_uri: {db_uri} ex_id: {db_uri}")
    client = pymongo.MongoClient(db_uri)
    if agave is None:
        agave = Agave.restore()
    
    # The view runs only RUNNING pipeline jobs
    etjv = client.catalog_staging.experiment_tapis_jobs_view
    experiments = etjv.find({"_id.experiment_id": ex_id})
    jobs_map = {}
    for e in experiments:
        jobs = e["jobs"]
        for j in jobs:
            #print(f"j: {j}")
            for tj in j["agave_jobs"]:
                #print(f"tj: {tj}")
                try:
                    tjob = agave.jobs.get(jobId=tj)
                    if tjob.status in ["RUNNING"]:
                        if j["pipeline_name"] not in jobs_map:
                            jobs_map[j["pipeline_name"]] = []
                        analysis = j["analysis"] if "analysis" in j else None
                        jobs_map[j["pipeline_name"]].append([analysis, tj])
                except Exception as exc:
                    print(f"exc: {exc}")
    return jobs_map

def get_tapis_jobs_for_experiment_reference(db_uri, ex_ref, agave=None):
    client = pymongo.MongoClient(db_uri)
    sr = client.catalog_staging.structured_requests
    matches = sr.find({"experiment_reference":ex_ref})
    jobs_map = {}
    if matches.count() == 1: # no children
        ex = matches[0]
        jobs_map = get_tapis_jobs_for_experiment(db_uri, ex["experiment_id"], agave)
    else:
        for ex in matches:
            jm = get_tapis_jobs_for_experiment(db_uri, ex["experiment_id"])
            for k, v in jm.items():
                if k in jobs_map:
                    jobs_map[k].extend(v)
                else:
                    jobs_map[k] = v
    return jobs_map

def stop_tapis_jobs(jobs_map, pipelines, analysis=None):
    agave = Agave.restore()
    for p in pipelines:
        tapis_jobs = jobs_map[p] if p in jobs_map else []
        for tj in tapis_jobs:
            if analysis is None or p == "Precomputed data table" and analysis == tj[0]:
                try:
                    print(f"stopping job {tj[1]}")
                    agave.jobs.manage(jobId=tj[1], body={"action":"stop"})
                except Exception as exc:
                    print(f"exc: {exc}")
    
def main():
    if len(sys.argv) < 2:
        print('python tapis_job_cleanup.py db_uri')
        sys.exit(2)

    print(sys.argv[1])
    #jobs_map = get_tapis_jobs_for_experiment_reference(sys.argv[1], "NovelChassis-Endogenous-Promoter")
    jobs_map = get_tapis_jobs_for_experiment_reference(sys.argv[1], "YeastSTATES-Dual-Response-CRISPR-Short-Duration-Time-Series-30C", Agave.restore())
    print(f"jobs_map: {jobs_map}")
    #stop_tapis_jobs(jobs_map, ["Precomputed data table"])
  
if __name__ == '__main__':
  main() 
