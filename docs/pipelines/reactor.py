from reactors.runtime import Reactor, agaveutils
from datacatalog.pipelinejobs import PipelineJob

def main():

    rx = Reactor()
    m = rx.context.message_dict

    job = PipelineJob(rx, 'transcriptic', 'Yeast-Gates', 'sample.transcriptic.aq1btsj94wghbk',
                      'measurement.transcriptic.sample.transcriptic.aq1btsj94wghbk.2')

    job.setup(data=m)
    # Set up and launch Agave jobs with callbacks based on job.callback

    job_def = {'appId': 'hello-agave-cli-0.1.0u1',
               'notifications': [
                   {'event': '*',
                    'persistent': False,
                    'url': job.callback + '&status=${STATUS}'}]}

    try:
        resp = rx.client.jobs.submit(body=job_def)

        job_id = None
        if 'id' in resp:
            job_id = resp['id']
            job.running({'launched': job_id})
        else:
            job.fail()
    except Exception as exc:
        job.cancel()
        rx.on_failure('Failed to launch pipeline', exc)

if __name__ == '__main__':
    main()

