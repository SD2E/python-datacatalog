.. _reactormanagedpipelinejob:

=========================
ReactorManagedPipelineJob
=========================

The ``ReactorManagedPipelineJob`` class provides the same create-and-manage
functions as ``ManagedPipelineJob``, but leverages the Reactors
client-side environment to simplify initialization.

Configuration
-------------

Like ``ManagedPipelineJob``, this class interacts with Agave API, SD2 MongoDB,
and the PipelineJobs Manager to launch a job, but the configuration is taken
from the Reactor's ``config.yml`` and environment variables. Inside a Reactor (
based on the ``sd2e/reactors:python3-edge``), configuration is as follows:

.. code-block:: python

   from datacatalog.managers.pipelinejobs import ReactorManagedPipelineJobInstance
   rx = Reactor()
   # pass additional keyword arguments like experiment_id or instanced
   # after `data`
   rmpj = ReactorManagedPipelineJob(rx, data={}, ...)
   rmpj.setup()
   # Get the job's callback URL
   my_callback = rmpj.callback
   # Send an event
   rmpj.run()

.. note:: Make sure to have a plan to capture and propagate ``update_token``
          returned by any PipelineJob actions or events. It will be required
          for future updates and it may change after an unspecified number
          of uses.

Parameterization
----------------

See documentation for :doc:`managedpipelinejob` to see additional run-time
parameterization options for this class.

Sending Events
--------------

All job events inherit a named method from ``ManagedPipelineJob``. Thus,
sending an event looks like so:

.. code-block:: python

   # just send 'run'
   rmpj.run(data={'Job is now running!'})
   # chain 'run' and 'update'
   rmpj.run(data={'msg': 'Job is still running!'}).update(data={'msg': 'This is an update'})

Canceling a Job
---------------

As with ``ManagedPipelineJob``, this class can cancel a job until it has
progressed to the **RUNNING** state.

.. code-block:: python

   # cancel the job
   rmpj.cancel()

Resetting a Job
---------------

As with ``ManagedPipelineJob``, this class can reset a job to its original
**CREATED** state, erasing contents of the job's archive path in the process.
This action requires an administrator-level token.

.. code-block:: python

   # cancel the job
   admin_tok = 'ka5r54v83dmp3tf8'
   rmpj.reset(token=admin_tok)

Deleting a Job
--------------

As with ``ManagedPipelineJob``, this class can delete a job. At present,
the job's archive path and contents are preserved. This action requires
an administrator-level token.

.. code-block:: python

   # cancel the job
   admin_tok = 'ka5r54v83dmp3tf8'
   rmpj.delete(token=admin_tok)
