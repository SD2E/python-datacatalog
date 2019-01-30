.. _managedpipelinejob:

==================
ManagedPipelineJob
==================

The Python3 class ``datacatalog.managers.pipelinejobs.ManagedPipelineJob``
provides all the critical job management and metadata linkage functionality.
Other methods build on it, providing alternative interfaces suited to
particular use cases.

Configuration
-------------

The class interacts with Agave API, SD2 MongoDB, and the PipelineJobs Manager
Reactor. Configuration details for these resources can be passed like so:

.. code-block:: pycon

  from datacatalog.managers.pipelinejobs import ManagedPipelineJob
  from agavepy.agave import Agave

   mongodb={'authn': 'bW9uZ29kYjov...jRWJTI2SCUyQiy1zdGFnIwL2W1hcnk='}
   pipelines={'job_manager_id': 'G1p783PxpalBB',
              'job_manager_nonce': 'SD2E_G1p783PxpalBB',
              'pipeline_uuid': '1064aaf1-459c-5e42-820d-b822aa4b3990'}
   agave_client=Agave.restore()
   mpj = ManagedPipelineJob(mongodb, pipelines, agave=agave_client, ...)

.. warning:: Never actually include the value for ``job_manager_nonce`` in a
   public source repository or Docker image.

Parameterization
----------------

*Coming soon*

Sending Events
--------------

All job events have a corresponding method in ``ManagedPipelineJob``. Calling an
event method will cause the job to attempt a state transition. If an invalid
transition is requested, a ``transitions.core.MachineError`` will be raised.
Otherwise, the job's state will change and the event appended to the job's
history. Events can be sent with an optional ``data`` dictionary which will be
attached to the event in the history. Event methods can be chained, so long as
doing so does not violate allowable state transitions.

.. code-block:: pycon

   # just send 'run'
   >>> mpj.run(data={'Job is now running!'})
   # chain 'run' and 'update'
   >>> mpj.run(data={'msg': 'Job is still running!'}).update(data={'msg': 'This is an update'})
   # send 'finish'
   >>> mpj.finish()
   # try to send 'run' again and watch the firewworks
   >>> mpj.run()
   Traceback (most recent call last):
   File "<stdin>", line 1, in <module>
   transitions.core.MachineError: 'Cannot transition to RUNNING from FINISHED'

Canceling a Job
---------------

A PipelineJob may be canceled until it processes an a event. If the job has not
yet entered a ``RUNNING`` or ``FAILED`` state, do the following to deletes the
nascent job record from the Data Catalog.

.. code-block:: pycon

   # cancel the job
   >>> mpj.cancel()

If A job needs to be marked as unsuccessful after beginning its lifecycle,
the only recourse (barring administrator intervention) is via ``job.fail()``.
Cancelling an active job will result in a ``ManagedPipelineJobError``
exception. This design helps ensure an adequate record is maintained of all
computational work managed by the system.

Failing a PipelineJob
~~~~~~~~~~~~~~~~~~~~~

As mentioned above, ``FAILED`` is a valid terminal state. Set it by sending the
**fail** event.

.. code-block:: pycon

   mpj.fail()
   print(mpj.state)
   >>> 'FAILED'

Deferred Updates
----------------

It is possible to update a job's status after the initiating process has
exited, so long as the job's current **update_token** is known. If it is
included in a future message by another process, either as a property in a
JSON message or as a

ManagedPipelineJobInstance

Overview
~~~~~~~~

The Pipelines system leverages Agave's event-driven notification and Abaco's rich callback support to let Agave jobs update the status of the PipelineJob created by the Reactor that spawned them. It is equally possible for other Reactors (or even future executions of the current Reactor) to update PipelineJobs as well. Rather than relying on persisent database connnections, this is accomplished this by a event system implemented in the ``pipeline-jobs-manager`` Reactor `(documented here) <https://gitlab.sd2e.org/sd2program/pipeline-jobs-manager>`_.

Update from an Agave Job
~~~~~~~~~~~~~~~~~~~~~~~~

Let's assume we have a Reactor `fcs-reactor` that coordinates execution of an Agave job using the app `fcs-etl-0.4.0u16`. The Reactor already has code to generate a job definition from a template and can generate a JSON job definition that resembles this example.

.. code-block:: json

   {
     "name": "FCS ETL processing job",
     "inputs": {"inputData": "agave://data-sd2e-community/transcriptic/yeast-gates_q0/r1bbq4mr76ngd/3/instrument_output"},
     "archiveSystem": "data-sd2e-community",
     "archivePath": "/transcriptic/yeast-gates_q0/r1bbq4mr76ngd/3/processed/fcs-etl-0.4.0u2/20180710-1430-proven-pig",
     "appId": "fcs-etl-0.4.0u2",
     "batchQueue": "normal",
     "maxRunTime": "12:00:00",
     "archive": true,
     "notifications": [
       {
         "url": "notifications@sd2e.org",
         "event": "FINISHED",
         "persistent": false
       },{
         "url": "notifications@sd2e.org",
         "event": "FAILED",
         "persistent": false
       }]}

We can enable this job to update a PipelineJob with one addition to ``notifications``:

.. code-block:: json

   {
      "url": "https://api.sd2e.org/actors/v2/G56vjoAVzGkkq/messages?x-nonce=SD2E_XqsfKLFd3nrN&token=940a5adc78720505&uuid=58fa9ec7-6c25-5525-94f3-e853335e2f17&status=${STATUS}",
      "event": "*",
      "persistent": false
   }

**Explanation:** Actor ``G56vjoAVzGkkq`` is the ``pipeline-jobs-manager``. The url parameters encode event and authorization details: The ``x-nonce`` parameter lets the job send a message to ``G56vjoAVzGkkq``, ``token`` is a job-specific password with a duration of 72 hours, ``uuid`` is the job's unique identifier, and ``status`` is the Agave API job status. We set ``event`` to ``*`` which means that all events from the job are sent to ``pipeline-jobs-manager``, and we set ``persistent`` to false so that only the first instance of any job state change is transmitted. The ``pipeline-jobs-manager`` reactor maps Agave API job states to their relevant PipelineJob event names and processes them as such. Specifically, it sends the named event to the PipelineJob along with the entire body of the Agave jobs callback POST as the ``data`` payload.

Update from a Reactor
~~~~~~~~~~~~~~~~~~~~~

Updating a PipelineJob's status from the original actor (but in a different execution) or from another actor is as simple as sending a message to ``pipeline-jobs-manager``. The message must conform to (and is validated against) the ``PipelineJobEvent`` schema documented below. Here is an example:

.. code-block:: python

   rx = Reactor()
   event_msg = {'uuid': '58fa9ec7-6c25-5525-94f3-e853335e2f17',
      'event': 'update',
      'data': {'key4': 'value4'}
      'token': '940a5adc78720505'}
   rx.send_message('G56vjoAVzGkkq', event_msg)

**Explanation:** Reactor ``G56vjoAVzGkkq`` willl handle the job management task on your behalf.

The current JSON schema for PipelineJob events is as follows:

.. literalinclude:: event.jsonschema
   :language: json
