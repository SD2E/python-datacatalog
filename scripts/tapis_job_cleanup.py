import pymongo
import sys
from agavepy.agave import Agave

def get_tapis_jobs_for_experiment(db_uri, ex_id, agave=None):
    print(f"checking ex_id: {ex_id}")
    client = pymongo.MongoClient(db_uri)
    if agave is None:
        agave = Agave.restore()
    
    # The view contains only RUNNING pipeline jobs
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
                    if tjob.status in ["RUNNING", "BLOCKED"]:
                        if j["pipeline_name"] not in jobs_map:
                            jobs_map[j["pipeline_name"]] = []
                        analysis = j["analysis"] if "analysis" in j else None
                        jobs_map[j["pipeline_name"]].append([analysis, tj])
                except Exception as exc:
                    print(f"j: {j} exc: {exc}")
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
            jm = get_tapis_jobs_for_experiment(db_uri, ex["experiment_id"], agave)
            for k, v in jm.items():
                if k in jobs_map:
                    jobs_map[k].extend(v)
                else:
                    jobs_map[k] = v
    return jobs_map

def stop_tapis_jobs(jobs_map, pipelines, analysis=None, agave=None):
    if agave is None:
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
    agave = Agave.restore()
    jobs_map = get_tapis_jobs_for_experiment_reference(sys.argv[1], "NovelChassis-Endogenous-Promoter", agave=agave)
    #jobs_map = get_tapis_jobs_for_experiment(sys.argv[1], ex_id = "experiment.transcriptic.r1f7aux4qxty6b", agave=agave)
    print(f"jobs_map: {jobs_map}")
    stop_tapis_jobs(jobs_map, ["Precomputed data table"], agave=agave)
  
if __name__ == '__main__':
  main() 
