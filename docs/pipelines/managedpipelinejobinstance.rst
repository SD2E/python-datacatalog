.. _managedpipelinejobinstance:

==========================
ManagedPipelineJobInstance
==========================

The Python3 class ``ManagedPipelineJobInstance`` provides similar function to
``ManagedPipelineJob`` but for an existing PipelineJob.

Configuration
-------------

The class interacts with Agave API, SD2 MongoDB, and the PipelineJobs Manager
Reactor. Configuration details for these resources can be passed like so:

.. code-block:: pycon

   from datacatalog.managers.pipelinejobs import ManagedPipelineJobInstance

   job_uuid='1071269f-b251-5a5f-bec1-6d7f77131f3f'
   job_token='a3b29f2c62ec9d15'
   mongodb={'authn': 'bW9uZ29kYjov...jRWJTI2SCUyQiy1zdGFnIwL2W1hcnk='}

   mpj = ManagedPipelineJobInstance(mongodb, job_uuid, token=token, ...)

.. note:: Make sure to have a plan to capture and propagate ``update_token``
          returned by any PipelineJob actions or events. It will be required
          for future updates and it may change after an unspecified number
          of uses.

Parameterization
----------------

Beyond specifying `job_uuid`, no additional parameterization of this
class is permitted.

Sending Events
--------------

Send events as Python dicts to update the job state. All state transition rules
continue to apply.

.. code-block:: pycon

   event = {'name': 'update',
            'data': {'msg': 'update message'},
            'uuid': '1071269f-b251-5a5f-bec1-6d7f77131f3f',
            'token': 'a3b29f2c62ec9d15'}
   resp = mpj.handle(event)
   print(resp['token'])

Canceling a Job
---------------

Canceling a job is not possible using this class.

