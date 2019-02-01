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
   mpj.setup()

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

Resetting a PipelineJob
-----------------------

A job may be rolled back to its initial ``CREATED`` state, provided a valid
administrator-class token is passed with the request. The standard update
token associated with the job cannot authorize a reset action.

.. code-block:: pycon

   mpj.reset(token='rkz78NEcsD7ZmhVc')
   print(mpj.state)
   >>> 'CREATED'

The contents of the terminal directory in the job's archive path, but not the
directory itself is remains.

Deleting a PipelineJob
----------------------

A job may be deleted entirely (including references to it in the linkage fields
of the other LinkedStore documents), but only by passing an administrator-class
token to authorize the action.

.. code-block:: pycon

   mpj.delete(token='rkz78NEcsD7ZmhVc')

Currently, the job archive path and its contents are left intact.

Deferred Updates
----------------

It is possible to update a job's status after the initiating process has
exited, so long as the job's current **token** is known. The token must be
included in JSON messages to ``ManagedPipelineJobInstance`` or in web
service callbacks posted to the Jobs Manager Reactor.

